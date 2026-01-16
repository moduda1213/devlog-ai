import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.repository import Repository
from app.models.devlog import DevLog

@pytest.mark.asyncio
async def test_create_devlog(db_session):
    """DevLog 생성 및 JSON 필드 테스트"""
    # 1. User & Repository 생성
    user = User(github_username="logger", github_user_id=3003, access_token_encrypted="tok")
    db_session.add(user)
    await db_session.commit()
    
    repo = Repository(user_id=user.id, repo_name="logger/daily", repo_url="http://gh.com")
    db_session.add(repo)
    await db_session.commit()

    # 2. DevLog 생성
    today = date(2025, 1, 15)
    log = DevLog(
        user_id=user.id,
        repository_id=repo.id,
        date=today,
        summary="Today I learned FastAPI testing",
        main_tasks=["Setup pytest", "Write test cases"],
        learned_things=["AsyncSQLAlchemy", "Factory Boy is useful"],
        commit_count=5
    )
    db_session.add(log)
    await db_session.commit()

    # 3. 조회 및 검증
    await db_session.refresh(log)
    assert log.id is not None
    assert log.date == today
    assert log.main_tasks == ["Setup pytest", "Write test cases"]  # JSON 필드 자동 변환 확인
    assert log.commit_count == 5

@pytest.mark.asyncio
async def test_devlog_unique_constraint_per_day(db_session):
    """하루에 하나의 일지만 생성 가능 제약조건 테스트"""
    # 1. User & Repo 준비
    user = User(github_username="daily_user", github_user_id=4004, access_token_encrypted="tok")
    db_session.add(user)
    await db_session.commit()
    
    repo = Repository(user_id=user.id, repo_name="daily/repo", repo_url="http://gh.com")
    db_session.add(repo)
    await db_session.commit()

    target_date = date(2025, 5, 5)

    # 2. 첫 번째 일지 생성
    log1 = DevLog(
        user_id=user.id,
        repository_id=repo.id,
        date=target_date,
        summary="First log",
        main_tasks=[],
        learned_things=[]
    )
    db_session.add(log1)
    await db_session.commit()

    # 3. 같은 날짜에 두 번째 일지 생성 시도
    log2 = DevLog(
        user_id=user.id,
        repository_id=repo.id,
        date=target_date,  # 날짜 중복!
        summary="Duplicate log",
        main_tasks=[],
        learned_things=[]
    )
    db_session.add(log2)

    # 4. IntegrityError 발생 확인
    with pytest.raises(IntegrityError):
        await db_session.commit()
    
    await db_session.rollback()
