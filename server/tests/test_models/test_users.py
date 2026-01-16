import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User

@pytest.mark.asyncio
async def test_create_user(db_session):
    """User 생성 및 조회 테스트"""
    # Given
    new_user = User(
        github_username="test_octocat",
        github_user_id=123456,
        access_token_encrypted="encrypted_access_token_mock"
    )
    
    # When
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    # Then
    assert new_user.id is not None
    assert new_user.github_username == "test_octocat"
    
    # DB 재조회 확인
    stmt = select(User).where(User.github_username == "test_octocat")
    result = await db_session.execute(stmt)
    fetched_user = result.scalar_one_or_none()
    
    assert fetched_user is not None
    assert fetched_user.github_user_id == 123456

@pytest.mark.asyncio
async def test_user_unique_constraint(db_session):
    """User 유니크 제약조건(username, user_id) 테스트"""
    # 1. 첫 번째 유저 생성
    user1 = User(
        github_username="duplicate_user",
        github_user_id=99999,
        access_token_encrypted="token_1"
    )
    db_session.add(user1)
    await db_session.commit()

    # 2. 동일한 username을 가진 유저 생성 시도
    user2 = User(
        github_username="duplicate_user",  # 중복!
        github_user_id=88888,              # ID는 다름
        access_token_encrypted="token_2"
    )
    db_session.add(user2)
    
    # 3. IntegrityError 발생 확인
    with pytest.raises(IntegrityError):
        await db_session.commit()
    
    await db_session.rollback() # 세션 정리
