import httpx
import asyncio
from datetime import date, datetime, time
from loguru import logger
from app.core.config import settings

# --- 사용자 정의 예외 클래스 ---
class GithubApiError(Exception):
    """GitHub API 관련 기본 에러"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class GithubAuthError(GithubApiError):
    """401: 인증 실패"""
    def __init__(self, message: str = "Invalid GitHub credentials"):
        super().__init__(message, status_code=401)

class GithubRateLimitError(GithubApiError):
    """403/429: API 요청 제한 초과"""
    def __init__(self, message: str = "GitHub API rate limit exceeded"):
        super().__init__(message, status_code=429)

class GithubResourceNotFoundError(GithubApiError):
    """404: 리소스 없음"""
    def __init__(self, message: str = "GitHub resource not found"):
        super().__init__(message, status_code=404)

class GithubNoCommitsError(GithubApiError):
    """검색된 커밋이 없음 (R-BIZ-3)"""
    def __init__(self, message: str = "No commits found"):
        super().__init__(message, status_code=400) # Bad Request

GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

def _handle_github_error(e: httpx.HTTPStatusError):
    """HTTP 상태 코드에 따른 예외 매핑"""
    status_code = e.response.status_code
    error_msg = f"GitHub API Error: {str(e)}"
    
    if status_code == 401:
        raise GithubAuthError()
    
    elif status_code == 403 or status_code == 429:
        raise GithubRateLimitError()
    
    elif status_code == 404:
        raise GithubResourceNotFoundError()
    
    else:
        raise GithubApiError(message=error_msg, status_code=status_code)

async def get_access_token(code: str) -> str:
    """GitHub 인증 코드를 Access Token으로 교환"""
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        }
        try:
            response = await client.post(GITHUB_TOKEN_URL, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise GithubAuthError(message=data["error_description"])
            
            return data["access_token"]
        
        except httpx.HTTPStatusError as e:
            _handle_github_error(e)
            
        except httpx.RequestError as e:
            raise GithubApiError(message=f"Network error: {str(e)}")

async def get_user_info(access_token: str) -> dict:
    """Access Token으로 GitHub 사용자 정보 조회"""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            response = await client.get(GITHUB_USER_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            _handle_github_error(e)
            
        except httpx.RequestError as e:
            raise GithubApiError(message=f"Network error: {str(e)}")
        
async def get_repositories(
    access_token: str,
    page: int = 1,
    per_page: int = 10
) -> list[dict]:
    """
    사용자의 GitHub 저장소 목록 조회
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        safe_per_page = min(per_page, 100)
        
        params = {
            "sort": "updated",
            "direction": "desc",
            "type": "owner",
            "page": page,
            "per_page": safe_per_page
        }
        try:
            response = await client.get("https://api.github.com/user/repos", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            _handle_github_error(e)
        except httpx.RequestError as e:
            raise GithubApiError(message=f"Network error: {str(e)}")

async def fetch_commits(
    repo_name: str,
    target_date: date,
    access_token: str
) -> list[dict]:
    """
    특정 날짜의 커밋 목록 수집 및 상세 정보(patch) 포함 (R-BIZ-3)

    Args:
        repo_name: 저장소 풀네임 (예: "user/repo")
        target_date: 조회 대상 날짜
        access_token: GitHub OAuth 토큰

    Returns:
        상세 정보(files, patch, stats)가 포함된 커밋 리스트

    Raises:
        GithubNoCommitsError: 커밋이 없는 경우
        GithubApiError: API 호출 실패 시
    """
    logger.info(f"🔍 [GitHub] 상세 커밋 수집 시작: {repo_name} | 날짜: {target_date}")

    # 상세 조회를 위해 타임아웃을 넉넉하게 설정
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 1. 커밋 목록(SHA) 조회
        since = datetime.combine(target_date, time.min).isoformat() + "Z"
        until = datetime.combine(target_date, time.max).isoformat() + "Z"

        list_url = f"https://api.github.com/repos/{repo_name}/commits"
        params = {"since": since, "until": until, "per_page": 100}

        try:
            response = await client.get(list_url, headers=headers, params=params)
            response.raise_for_status()
            base_commits = response.json()

            if not base_commits:
                raise GithubNoCommitsError(f"No commits found for {target_date}")

            # 2. 각 커밋 SHA에 대해 상세 정보 병렬 수집 (asyncio.gather)
            logger.debug(f"📶 {len(base_commits)}개 커밋 상세 정보 병렬 조회 중...")

            tasks = [
                client.get(f"{list_url}/{commit['sha']}", headers=headers)
                for commit in base_commits
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            detailed_commits = []
            for resp in responses:
                if isinstance(resp, httpx.Response) and resp.status_code == 200:
                    data = resp.json()

                    # ✨ [최적화] AI 분석용 파일 데이터 정제
                    optimized_files = []
                    for f in data.get("files", []):
                        filename = f["filename"]
                        patch = f.get("patch", "")
                        status = f["status"]

                        # 1. 분석 가치가 없는 파일 제외 (Lock 파일, 이미지, 바이너리 등)
                        if any(filename.endswith(ext) for ext in ['.lock', '.png', '.jpg', '.svg', '.pdf', '.min.js']):
                            continue

                        # 2. Patch 길이 제한 (토큰 폭발 방지)
                        # 새로 추가된 파일이거나 내용이 너무 길면 요약 처리
                        if status == 'added' and len(patch) > 300:
                            patch = "(new file content hidden)"
                        elif len(patch) > 500:
                            patch = patch[:500] + "\n...(truncated)"

                        optimized_files.append({
                            "filename": filename,
                            "status": status,
                            "patch": patch
                        })

                    # ✨ [최적화] 핵심 정보만 남김 (sha, author 등 제거)
                    detailed_commits.append({
                        "message": data["commit"]["message"],
                        "files": optimized_files
                    })

                elif isinstance(resp, Exception):
                    logger.error(f"❌ 커밋 상세 조회 실패: {str(resp)}")

            logger.info(f"✅ {len(detailed_commits)}개의 상세 커밋 데이터 수집 완료 (AI 최적화됨)")
            return detailed_commits

        except httpx.HTTPStatusError as e:
            _handle_github_error(e)
        except httpx.RequestError as e:
            raise GithubApiError(message=f"Network error: {str(e)}")