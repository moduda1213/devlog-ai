import pytest
from datetime import date
from unittest.mock import patch
from httpx import AsyncClient

from app.services.github_service import GithubNoCommitsError

# Mock 데이터
MOCK_COMMITS = [
    {
        "message": "feat: add journal api",
        "files": [
            {
                "filename": "api.py",
                "status": "modified",
                "additions": 10,
                "deletions": 2,
                "patch": "..."
            }
        ]
    }
]

MOCK_GEMINI_RESPONSE = {
    "summary": "일지 API를 구현했습니다.",
    "main_tasks": ["Journal 스키마 정의", "API 라우터 구현"],
    "learned_things": ["FastAPI 의존성 주입 패턴"]
}

@pytest.mark.asyncio
async def test_create_journal_success(
    async_client: AsyncClient, 
    test_user, 
    test_repo, # conftest.py에 fixture 추가 필요 (아래 설명 참조)
    access_token_header
):
    """일지 생성 성공 테스트 (Mocking)"""
    
    # 1. Service Mocking
    with patch("app.services.journal_service.fetch_commits", return_value=MOCK_COMMITS) as mock_fetch, \
         patch("app.services.gemini_service.GeminiService.generate_journal", return_value=MOCK_GEMINI_RESPONSE) as mock_generate:
        # 2. API 호출
        today = date.today().isoformat()
        response = await async_client.post(
            "/api/v1/journals/",
            params={"date": today},
            headers=access_token_header
        )
        # 3. 검증
        assert response.status_code == 201
        data = response.json()
        assert data["summary"] == MOCK_GEMINI_RESPONSE["summary"]
        assert data["commit_count"] == 1
        assert data["lines_added"] == 10
        # Mock 호출 검증
        mock_fetch.assert_called_once()
        mock_generate.assert_called_once()
        
@pytest.mark.asyncio
async def test_create_journal_no_commits(
    async_client: AsyncClient,
    test_user,
    test_repo,
    access_token_header
):
    """커밋이 없는 경우 400 에러 테스트"""
    with patch("app.services.journal_service.fetch_commits", side_effect=GithubNoCommitsError()):
        response = await async_client.post(
            "/api/v1/journals/",
            headers=access_token_header
        )
        assert response.status_code == 400
        assert "No commits found" in response.json()["detail"]