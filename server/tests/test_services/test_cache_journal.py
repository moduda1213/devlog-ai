import pytest
import json
from app.services.journal_service import JournalService
from app.schemas.journal import JournalUpdate
@pytest.mark.asyncio
async def test_get_journal_detail_cache_miss_and_hit(
    db_session,
    mock_redis,
    test_journal,
    test_user
):
    """
    시나리오:
    1. 첫 조회 -> Cache Miss -> DB 조회 -> Cache Set
    2. 두 번째 조회 -> Cache Hit -> Redis 값 반환
    """
    service = JournalService(db_session, mock_redis)
    journal_id = test_journal.id
    user_id = test_user.id
    cache_key = f"journal:{user_id}:{journal_id}"
    # 1. 첫 번째 조회 (Cache Miss)
    # Redis가 비어있는지 확인
    assert await mock_redis.get(cache_key) is None
    result1 = await service.get_journal_detail(user_id, journal_id)
    assert result1 is not None
    assert result1.id == journal_id
    # 캐시가 생성되었는지 확인
    cached_data = await mock_redis.get(cache_key)
    assert cached_data is not None
    # 캐시된 데이터 내용 확인
    assert json.loads(cached_data)["id"] == str(journal_id)
    # 2. 두 번째 조회 (Cache Hit)
    result2 = await service.get_journal_detail(user_id, journal_id)
    # 캐시 Hit 시 dict 반환 (JournalService 구현에 따름)
    # 만약 Pydantic 모델 반환으로 구현했다면 타입 체크 변경 필요
    assert isinstance(result2, dict)
    assert result2["id"] == str(journal_id)
    assert result2["summary"] == test_journal.summary
@pytest.mark.asyncio
async def test_update_journal_invalidates_cache(
    db_session,
    mock_redis,
    test_journal,
    test_user
):
    """일지 수정 시 캐시 삭제(Invalidate) 테스트"""
    service = JournalService(db_session, mock_redis)
    journal_id = test_journal.id
    user_id = test_user.id
    cache_key = f"journal:{user_id}:{journal_id}"
    # 미리 캐시 세팅 (강제)
    await mock_redis.set(cache_key, "dummy_data")
    assert await mock_redis.get(cache_key) == "dummy_data"
    # 수정 수행
    update_data = JournalUpdate(summary="Updated Summary Cache Test")
    await service.update_journal(user_id, journal_id, update_data)
    # 캐시가 삭제되었는지 확인
    assert await mock_redis.get(cache_key) is None