import pytest
import respx
from httpx import Response
from datetime import date
from app.services.github_service import fetch_commits, GithubNoCommitsError

# Mock 데이터
MOCK_COMMITS = [
    {
        "sha": "123456",
        "commit": {
            "message": "feat: init project",
            "author": {"name": "test_user", "date": "2025-01-19T10:00:00Z"}
        }
    }
]

MOCK_COMMIT_DETAIL = {
    "sha": "123456",
    "commit": {
        "message": "feat: init project",
        "author": {"name": "test_user", "date": "2025-01-19T10:00:00Z"}
    },
    "stats": {"total": 10, "additions": 7, "deletions": 3},
    "files": [
        {
            "filename": "app/main.py",
            "status": "added",
            "additions": 7,
            "deletions": 3,
            "patch": "+ print('hello')" # 이 데이터가 핵심!
        }
    ]
}

@pytest.mark.asyncio
async def test_fetch_commits_success():
    """커밋 목록 조회 성공 케이스"""
    target_date = date(2025, 1, 19)
    repo_name = "octocat/Hello-World"
    
    async with respx.mock:
        # 1. 커밋 목록 API Mocking
        respx.get(f"https://api.github.com/repos/{repo_name}/commits").mock(
            return_value=Response(200, json=MOCK_COMMITS)
        )

        # 2. 🔥 커밋 상세 API Mocking (추가된 부분)
        respx.get(f"https://api.github.com/repos/{repo_name}/commits/123456").mock(
            return_value=Response(200, json=MOCK_COMMIT_DETAIL)
        )

        commits = await fetch_commits(repo_name, target_date, "test_token")

        # 3. 검증 로직 강화
        assert len(commits) == 1
        # assert commits[0]["sha"] == "123456" # 최적화로 제거됨
        assert "files" in commits[0]
        assert commits[0]["files"][0]["patch"] == "+ print('hello')"

@pytest.mark.asyncio
async def test_fetch_commits_empty():
    """커밋이 없을 때 GithubNoCommitsError 발생 검증 (R-BIZ-3)"""
    target_date = date(2025, 1, 20)
    repo_name = "octocat/Hello-World"
    
    async with respx.mock:
        # 빈 리스트 반환 Mocking
        respx.get(f"https://api.github.com/repos/{repo_name}/commits").mock(
            return_value=Response(200, json=[])
        )
        # 예외 발생 확인
        with pytest.raises(GithubNoCommitsError):
            await fetch_commits(repo_name, target_date, "test_token")