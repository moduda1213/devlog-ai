from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cryptography.fernet import Fernet
from loguru import logger

from app.models.user import User
from app.core.config import settings

# 암호화 도구 초기화 (서비스 로딩 시 1회 실행)
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

async def get_or_create_user(
    db: AsyncSession, 
    github_id: int, 
    username: str, 
    access_token: str
) -> User:
    """
    GitHub 사용자 정보를 기반으로 사용자를 생성하거나 갱신합니다.
    Access Token은 암호화하여 저장합니다.
    
    Args:
        db: DB 세션
        github_id: GitHub 고유 ID
        username: GitHub 로그인 ID
        access_token: GitHub API 접근 토큰 (평문)
    Returns:
        생성/갱신된 User 객체
    """
    # 토큰 암호화
    encrypted_token = cipher_suite.encrypt(access_token.encode()).decode()
    try: 
        # DB 조회
        stmt = select(User).where(User.github_user_id == github_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            logger.debug(f"🔄 Updating existing user: {username} (ID: {github_id})")
            user.access_token_encrypted = encrypted_token
            user.github_username = username
            # user.updated_at은 SQLAlchemy onupdate에 의해 자동 갱신됨
            
        else:
            logger.info(f"✨ Creating new user: {username} (ID: {github_id})")
            user = User(
                github_user_id=github_id,
                github_username=username,
                access_token_encrypted=encrypted_token
            )
            db.add(user)
            
        await db.commit()
        await db.refresh(user)
        return user
    
    except Exception as e:
        await db.rollback()
        raise e