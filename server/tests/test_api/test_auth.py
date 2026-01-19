import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.core.security import create_access_token

# Mock 데이터
MOCK_GITHUB_USER = {
    "id": 12345,
    "login": "testuser",
    "email": "test@example.com"
}
MOCK_ACCESS_TOKEN = "gho_mock_access_token"

@pytest.mark.asyncio
async def test_github_login_redirect(async_client: AsyncClient):
    """
    [완료 기준 1] GitHub 로그인 버튼 클릭 시 GitHub 인증 페이지로 이동한다.
    """
    response = await async_client.get("/api/v1/auth/github/login")
    
    # 리다이렉트 응답 확인 (307 Temporary Redirect)
    assert response.status_code == 307
    assert "github.com/login/oauth/authorize" in response.headers["location"]
    assert "client_id=" in response.headers["location"]

@pytest.mark.asyncio
async def test_github_callback_success(async_client: AsyncClient):
    """
    [완료 기준 2] 인증 완료 후 DB에 사용자 정보가 저장/갱신된다.
    """
    # GitHub Service Mocking
    with patch("app.services.github_service.get_access_token", return_value=MOCK_ACCESS_TOKEN), \
         patch("app.services.github_service.get_user_info", return_value=MOCK_GITHUB_USER):
        
        response = await async_client.get("/api/v1/auth/github/callback?code=mock_code")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login Successful"
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_read_users_me_success(async_client: AsyncClient, test_user):
    """
    [완료 기준 3] /auth/me 호출 시 본인 정보를 반환한다.
    """
    # 테스트용 유저의 토큰 생성
    token = create_access_token(subject=test_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.github_username
    assert data["github_id"] == test_user.github_user_id

@pytest.mark.asyncio
async def test_read_users_me_unauthorized(async_client: AsyncClient):
    """
    [완료 기준 4] 인증되지 않은 요청은 401 에러를 반환한다.
    """
    # 헤더 없이 요청
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    
    # 잘못된 토큰으로 요청
    headers = {"Authorization": "Bearer invalid_token"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
