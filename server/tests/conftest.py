import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.database import Base

from app.models.user import User
from app.models.repository import Repository
from app.models.devlog import DevLog

# 테스트용 DB 엔진 (세션 스코프: 테스트 세션 내내 유지)
@pytest_asyncio.fixture(scope="session")
async def engine():
    # SQLite In-Memory DB 사용 (네트워크 문제 원천 차단)
    # check_same_thread=False: SQLite를 비동기 환경에서 사용할 때 필수 옵션
    test_db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        test_db_url, 
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # 1. 테이블 초기화 (기존 데이터 삭제)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 2. 테스트 종료 후 리소스 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

# 테스트용 DB 세션 (함수 스코프: 각 테스트마다 독립적)
@pytest_asyncio.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # 테스트 종료 후 롤백 (데이터 상태 원상복구)
        await session.rollback()
