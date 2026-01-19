import httpx
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
    특정 날짜의 커밋 목록 수집
    - R-BIZ-3: UTC 00:00:00 ~ 23:59:59 범위 검색
    - 커밋 0개 시 GithubNoCommitsError 발생
    """
    logger.info(f"Fetching commits for repository: {repo_name}, date: {target_date}")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        # UTC 기준 시간 범위 설정
        since = datetime.combine(target_date, time.min).isoformat() + "Z"
        until = datetime.combine(target_date, time.max).isoformat() + "Z"
        
        params = {
            "since": since,
            "until": until,
            "per_page": 100
        }
        
        url = f"https://api.github.com/repos/{repo_name}/commits"
        
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            commits = response.json()
            
            commit_count = len(commits)
            if commit_count == 0:
                logger.warning(f"No commits found for {repo_name} on {target_date}")
                raise GithubNoCommitsError(f"No commits found for {target_date}")
            
            logger.info(f"Found {commit_count} commits for {repo_name}")
            return commits
            
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API Error: {e.response.text}")
            _handle_github_error(e)
        except httpx.RequestError as e:
            logger.error(f"Network error fetching commits: {e}")
            raise GithubApiError(message=f"Network error: {str(e)}")