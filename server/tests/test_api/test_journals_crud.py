'''
   1. 권한 분리: 다른 사용자의 일지를 조회/수정/삭제할 수 없어야 합니다. (user_id 필터링 확인)
   2. 트랜잭션: 수정/삭제 중 에러 발생 시 DB에 반영되지 않아야 합니다.
   3. 페이지네이션: size 제한(최대 100)이 적용되어야 합니다
'''
import pytest
from httpx import AsyncClient
from app.models import Journal

@pytest.mark.asyncio
async def test_read_journals_pagination(
    async_client: AsyncClient,
    test_user_token: str,
    test_journal: Journal,  # conftest.py나 별도 fixture로 생성된 일지
):
    """일지 목록 조회 (페이지네이션) 테스트"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    journal_id = test_journal.id
    
    # 1. 목록 조회 요청
    response = await async_client.get(
        "/api/v1/journals/",
        params={"page": 1, "size": 10},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["size"] == 10
    
    items = data["items"]
    assert isinstance(items, list)
    assert len(items) >= 1
    # 조회된 일지 중 테스트 일지가 포함되어 있는지 확인
    assert any(j["id"] == str(journal_id) for j in items)
    
@pytest.mark.asyncio
async def test_read_journal_detail(
    async_client: AsyncClient,
    test_user_token: str,
    test_journal: Journal
):
    """일지 상세 조회 테스트"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    journal_id = test_journal.id
    
    response = await async_client.get(
        f"/api/v1/journals/{journal_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(journal_id)
    assert data["summary"] == test_journal.summary
    
@pytest.mark.asyncio
async def test_update_journal(
    async_client: AsyncClient,
    test_user_token: str,
    test_journal: Journal
):
    """일지 수정 테스트"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    journal_id = test_journal.id
    update_data = {
        "summary": "Updated Summary",
        "main_tasks": ["Updated Task 1", "Updated Task 2"]
    }
    response = await async_client.patch(
        f"/api/v1/journals/{journal_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Updated Summary"
    assert "Updated Task 1" in data["main_tasks"]
    
@pytest.mark.asyncio
async def test_delete_journal(
    async_client: AsyncClient,
    test_user_token: str,
    test_journal: Journal
):
    """일지 삭제 테스트"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    journal_id = test_journal.id
    # 1. 삭제 요청
    response = await async_client.delete(
        f"/api/v1/journals/{journal_id}",
        headers=headers
    )
    assert response.status_code == 204
    # 2. 삭제 확인 (상세 조회 시 404)
    get_response = await async_client.get(
        f"/api/v1/journals/{journal_id}",
        headers=headers
    )
    assert get_response.status_code == 404
    
@pytest.mark.asyncio
async def test_access_other_user_journal(
    async_client: AsyncClient,
    test_other_user_token: str,  # 타인의 토큰
    test_journal: Journal        # test_user(본인)의 일지
):
    """
    타인(test_other_user)이 test_user의 일지에 접근 시 
    404 Not Found (보안상 존재 여부 숨김) 또는 403 Forbidden 반환 검증
    현재 로직상 user_id 필터링으로 인해 404가 반환됨
    """
    headers = {"Authorization": f"Bearer {test_other_user_token}"}
    journal_id = test_journal.id
    
    # 1. 타인의 일지 상세 조회 시도
    response = await async_client.get(
        f"/api/v1/journals/{journal_id}",
        headers=headers
    )
    assert response.status_code == 404  # 내 일지가 아니므로 찾을 수 없음
    
    # 2. 타인의 일지 수정 시도
    response = await async_client.patch(
        f"/api/v1/journals/{journal_id}",
        json={"summary": "Hacked!"},
        headers=headers
    )
    assert response.status_code == 404

    # 3. 타인의 일지 삭제 시도
    response = await async_client.delete(
        f"/api/v1/journals/{journal_id}",
        headers=headers
    )
    assert response.status_code == 404