import pytest
import respx
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession


# GitHub API Mock 응답 데이터
MOCK_GITHUB_REPOS = [
    {
        "id": 12345,
        "name": "Hello-World",
        "full_name": "octocat/Hello-World",
        "html_url": "https://github.com/octocat/Hello-World",
        "description": "This is your first repo!",
        "private": False,
        "owner": {"login": "octocat"}
    },
    {
        "id": 67890,
        "name": "DevLog-AI",
        "full_name": "octocat/DevLog-AI",
        "html_url": "https://github.com/octocat/DevLog-AI",
        "description": "AI Developer Logger",
        "private": True,
        "owner": {"login": "octocat"}
    }
]

@pytest.mark.asyncio
async def test_get_repositories(
    async_client: AsyncClient, 
    test_user_token: str
):
    """
    [GET /repositories]
    GitHub API를 모킹하여 저장소 목록을 잘 받아오는지 테스트
    """
    # given: respx로 GitHub API 모킹
    async with respx.mock:
        respx.get("https://api.github.com/user/repos").mock(
            return_value=Response(200, json=MOCK_GITHUB_REPOS)
        )
        # when: API 호출
        response = await async_client.get(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        # then: 검증
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["full_name"] == "octocat/Hello-World"
        assert data[0]["is_selected"] is False # 초기엔 선택된게 없음
        
@pytest.mark.asyncio
async def test_select_repository(
    async_client: AsyncClient,
    test_user_token: str,
    db_session: AsyncSession
):
    """
    [POST /repositories/select]
    저장소 선택 시나리오 (R-BIZ-1 검증)
    """
    # 1. 첫 번째 저장소 선택
    payload = {
        "repo_name": "octocat/Hello-World",
        "repo_url": "https://github.com/octocat/Hello-World"
    }
    response = await async_client.post(
        "/api/v1/repositories/select",
        json=payload,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["repo_name"] == "octocat/Hello-World"
    assert data["is_selected"] is True
    
    # 2. 두 번째 저장소 선택 (기존 선택 해제 확인)
    payload_2 = {
        "repo_name": "octocat/DevLog-AI",
        "repo_url": "https://github.com/octocat/DevLog-AI"
    }
    response_2 = await async_client.post(
        "/api/v1/repositories/select",
        json=payload_2,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["repo_name"] == "octocat/DevLog-AI"
    assert data_2["is_selected"] is True
    
    # 3. DB 직접 확인 (첫 번째는 False, 두 번째는 True여야 함)
    # 주의: 테스트용 DB 세션은 격리되어 있을 수 있으므로, API 결과로 1차 검증하고
    # 확실히 하려면 GET /repositories를 다시 호출해보는 것이 좋음.
    async with respx.mock:
        respx.get("https://api.github.com/user/repos").mock(
            return_value=Response(200, json=MOCK_GITHUB_REPOS)
        )
        list_response = await async_client.get(
            "/api/v1/repositories",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        list_data = list_response.json()
        repo1 = next(r for r in list_data if r["full_name"] == "octocat/Hello-World")
        repo2 = next(r for r in list_data if r["full_name"] == "octocat/DevLog-AI")
        assert repo1["is_selected"] is False
        assert repo2["is_selected"] is True