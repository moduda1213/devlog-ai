import pytest
from datetime import datetime, timedelta, timezone
from app.services import auth_service
from app.models.refresh_token import RefreshToken
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_refresh_token(db_session, test_user): # ✅ user_fixture -> test_user
    user = test_user
    token = await auth_service.create_refresh_token(db_session, user.id)
    
    stmt = select(RefreshToken).where(RefreshToken.token_value == token)
    result = await db_session.execute(stmt)
    saved_token = result.scalar_one_or_none()
    
    assert saved_token is not None
    assert saved_token.user_id == user.id
    
    # ✅ [수정] DB 값(naive)에 UTC Timezone을 강제로 씌워서 비교
    expires_at = saved_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    assert expires_at > datetime.now(timezone.utc)

@pytest.mark.asyncio
async def test_verify_refresh_token_valid(db_session, test_user): # ✅ 수정
    # Given: 유효한 토큰 생성
    user = test_user
    token_value = await auth_service.create_refresh_token(db_session, user.id)
    
    # When: 검증
    token_obj = await auth_service.verify_refresh_token(db_session, token_value)
    
    # Then: 객체 반환
    assert token_obj is not None
    assert token_obj.token_value == token_value

@pytest.mark.asyncio
async def test_verify_refresh_token_expired(db_session, test_user): # ✅ 수정
    # Given: 만료된 토큰 생성 (강제 조작)
    user = test_user
    token_value = await auth_service.create_refresh_token(db_session, user.id)

    stmt = select(RefreshToken).where(RefreshToken.token_value == token_value)
    result = await db_session.execute(stmt)
    token_obj = result.scalar_one_or_none()

    token_obj.expires_at = datetime.now(timezone.utc) - timedelta(days=1) # 어제로 설정
    await db_session.commit()

    # When: 검증
    token_obj = await auth_service.verify_refresh_token(db_session, token_value)

    # Then: None 반환 및 DB 삭제 확인
    assert token_obj is None

    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_rotate_refresh_token(db_session, test_user): # ✅ 수정
    # Given: 기존 토큰
    user = test_user
    old_token = await auth_service.create_refresh_token(db_session, user.id)

    # When: Rotate
    new_refresh_token, _ = await auth_service.rotate_refresh_token(db_session, old_token)

    # Then: 새 토큰 발급, 기존 토큰 삭제
    assert new_refresh_token != old_token

    # 기존 토큰 DB 조회 -> 없어야 함
    stmt = select(RefreshToken).where(RefreshToken.token_value == old_token)
    assert (await db_session.execute(stmt)).scalar_one_or_none() is None

    # 새 토큰 DB 조회 -> 있어야 함
    stmt = select(RefreshToken).where(RefreshToken.token_value == new_refresh_token)
    assert (await db_session.execute(stmt)).scalar_one_or_none() is not None