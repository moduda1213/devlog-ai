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

@pytest.mark.asyncio
async def test_fetch_commits_success():
    """커밋 목록 조회 성공 케이스"""
    target_date = date(2025, 1, 19)
    repo_name = "octocat/Hello-World"
    
    async with respx.mock:
        # GitHub API Mocking
        respx.get(f"https://api.github.com/repos/{repo_name}/commits").mock(
            return_value=Response(200, json=MOCK_COMMITS)
        )
        commits = await fetch_commits(repo_name, target_date, "test_token")
        assert len(commits) == 1
        assert commits[0]["sha"] == "123456"

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