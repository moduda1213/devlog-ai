from redis.asyncio import Redis, from_url
from app.core.config import settings
from loguru import logger

async def get_redis_client() -> Redis | None:
    """Redis 클라이언트 생성 및 반환"""
    # 테스트 환경 등에서 REDIS_URL이 없을 경우를 대비해 예외처리 가능
    if not settings.REDIS_URL:
        logger.warning("REDIS_URL not set. Caching disabled.")
        return None
    
    try:
        redis = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # 연결 테스트
        await redis.ping()
        logger.info("✅Redis connected successfully")
        
        return redis
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        # Redis가 없어도 서비스는 돌아가야 하므로 None 반환
        return None

async def close_redis_client(redis: Redis):
    """Redis 연결 종료"""
    if redis:
        await redis.close()