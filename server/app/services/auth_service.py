import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.refresh_token import RefreshToken
from app.core.config import settings

async def create_refresh_token(db: AsyncSession, user_id: UUID) -> str:
    """
    Refresh Token 생성 및 DB 저장 (RTR 적용: 기존 토큰은 유지하되, 정책에 따라 다를 수 있음)
    여기서는 멀티 디바이스 로그인을 허용하기 위해 기존 토큰을 삭제하지 않고 추가합니다.
    """
    try:
        token_value = secrets.token_urlsafe(64) # 강력한 랜덤 문자열
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS) # 설정값 필요 (기본 14일)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token_value=token_value,
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        await db.commit()
        
        return token_value
    except Exception as e:
        await db.rollback()
        raise e

async def verify_refresh_token(db: AsyncSession, token_value: str) -> RefreshToken | None:
    """토큰 유효성 검증 및 만료 체크"""
    try:
        stmt = select(RefreshToken).where(RefreshToken.token_value == token_value)
        result = await db.execute(stmt)
        token = result.scalar_one_or_none()
        
        if not token:
            return None

        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            await db.delete(token)
            await db.commit()
            return None

        return token
    
    except Exception as e:
        await db.rollback()
        raise e

async def rotate_refresh_token(db: AsyncSession, old_token: str) -> str:
    """Refresh_token 교체"""
    # 1. 검증 및 객체 확보
    stmt = select(RefreshToken).where(RefreshToken.token_value == old_token)
    result = await db.execute(stmt)
    token_obj = result.scalar_one_or_none()
    
    if not token_obj:
        raise ValueError("Invalid refresh token")

    # 만료 체크 (UTC)
    expires_at = token_obj.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        await db.delete(token_obj)
        await db.commit()
        raise ValueError("Expired refresh token")

    user_id = token_obj.user_id
    
    # 2. 삭제
    await db.delete(token_obj)
    await db.commit() # 기존 토큰 삭제 확정
    
    # 3. 생성
    new_token = await create_refresh_token(db, user_id)
    return new_token, user_id
   
async def revoke_token(db: AsyncSession, token_value: str) -> None:
    """토큰 폐기 (로그아웃 시)"""
    try:
        stmt = delete(RefreshToken).where(RefreshToken.token_value == token_value)
        await db.execute(stmt)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise e