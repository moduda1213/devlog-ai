import uuid
from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis
from app.core.redis import get_redis_client, close_redis_client

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from sqlalchemy import select

# OAuth2 스키마 (Token URL은 실제로는 안 쓰지만 Swagger UI용으로 지정)
# 두 가지 보안 스키마 정의 (auto_error=False로 설정하여 하나가 없어도 즉시 에러 안 나게 함)
security_header = HTTPBearer(auto_error=False)
security_cookie = APIKeyCookie(name="access_token", auto_error=False)

async def get_current_user(
    token_auth: Annotated[HTTPAuthorizationCredentials | None, Depends(security_header)],
    token_cookie: Annotated[str | None, Depends(security_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    
    """JWT 토큰(헤더 또는 쿠키)을 검증하고 현재 사용자를 반환"""
       
    token = None
    
    # 우선순위 1: 헤더 (Authorization: Bearer <token>)
    if token_auth:
        token = token_auth.credentials
        
    # 우선순위 2: 쿠키 (access_token=Bearer <token>)
    elif token_cookie:
        # 쿠키 값에서 "Bearer " 접두사 제거 (포함되어 있다면)
        token = token_cookie.replace("Bearer ", "").strip()
           
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
           
    """JWT 토큰을 검증하고 현재 사용자를 반환"""
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        # ✅ 문자열을 UUID 객체로 변환
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")

    # DB에서 사용자 조회
    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

async def get_redis() -> AsyncGenerator[Redis | None, None]:
    redis = await get_redis_client()
    try:
        yield redis
    finally:
        close_redis_client(redis)