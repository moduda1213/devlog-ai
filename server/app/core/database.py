from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. 엔진 생성 (echo=True로 설정하면 SQL 쿼리가 로그에 출력됨)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 2. 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Base 클래스
class Base(DeclarativeBase):
    pass

# 4. 의존성 함수 (FastAPI Depends용)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session