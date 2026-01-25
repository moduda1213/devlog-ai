import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Journal, Repository, User

# -----------------------------------------------------------------------------
# Fixtures for Test Data
# -----------------------------------------------------------------------------

@pytest.fixture
async def stats_test_data(db_session: AsyncSession, test_user: User, test_repo: Repository):
    """통계 테스트를 위한 더미 데이터 생성 (Clean-up 후 생성)"""
    today = date.today()
    past_date = today - timedelta(days=3)
    
    # 1. 기존 데이터 정리 (테스트 간 충돌 방지)
    stmt = delete(Journal).where(
        Journal.user_id == test_user.id,
        Journal.date.in_([today, past_date])
    )
    await db_session.execute(stmt)
    await db_session.commit()
    
    # 2. 오늘 날짜 일지 (커밋 5개)
    j1 = Journal(
        user_id=test_user.id,
        repository_id=test_repo.id,
        date=today,
        summary="Today's work",
        main_tasks=["Task 1"],
        learned_things=["Thing 1"],
        commit_count=5,
        files_changed=3
    )
    
    # 3. 3일 전 일지 (커밋 3개)
    j2 = Journal(
        user_id=test_user.id,
        repository_id=test_repo.id,
        date=past_date,
        summary="Past work",
        main_tasks=["Task 2"],
        learned_things=["Thing 2"],
        commit_count=3,
        files_changed=2
    )

    db_session.add_all([j1, j2])
    await db_session.commit()
    return [j1, j2]

# -----------------------------------------------------------------------------
# Test Cases
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_weekly_stats(
    async_client: AsyncClient,
    access_token_header: dict,
    stats_test_data: list[Journal]
):
    """주간 통계 API 테스트"""
    response = await async_client.get(
        "/api/v1/stats/weekly",
        headers=access_token_header
    )

    assert response.status_code == 200
    data = response.json()

    # 1. 라벨 검증 (7일)
    assert len(data["labels"]) == 7

    # 2. 데이터셋 검증
    datasets = data["datasets"]
    commit_dataset = next((d for d in datasets if d["label"] == "Commits"), None)
    assert commit_dataset is not None

    # 총 커밋 수 검증 (5 + 3 = 8)
    total_commits = sum(commit_dataset["data"])
    assert total_commits == 8

@pytest.mark.asyncio
async def test_get_monthly_stats(
    async_client: AsyncClient,
    access_token_header: dict,
    stats_test_data: list[Journal]
):
    """월간 통계 API 테스트"""
    today = date.today()

    # 파라미터 없이 호출 (현재 연/월)
    response = await async_client.get(
        "/api/v1/stats/monthly",
        headers=access_token_header
    )

    assert response.status_code == 200
    data = response.json()

    # 1. 기본 정보 검증
    assert data["year"] == today.year
    assert data["month"] == today.month

    # 2. 요약 정보 검증
    assert data["total_commits"] == 8  # 5 + 3
    assert data["total_journals"] == 2

    # 3. 상세 기여 내역 검증
    contributions = data["contributions"]

    # 오늘 날짜의 기여도 찾기
    today_contrib = next((c for c in contributions if c["date"] == today.isoformat()), None)
    assert today_contrib is not None
    assert today_contrib["count"] == 5