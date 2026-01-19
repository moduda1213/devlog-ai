import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

from app.models.user import User
from app.core.security import create_access_token

# 테스트용 DB 엔진 (세션 스코프: 테스트 세션 내내 유지)
@pytest_asyncio.fixture(scope="session")
async def engine():
    # SQLite In-Memory DB 사용 (네트워크 문제 원천 차단)
    test_db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        test_db_url, 
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # 1. 테이블 초기화
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 2. 테스트 종료
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

# 테스트용 DB 세션 (함수 스코프: 각 테스트마다 독립적)
@pytest_asyncio.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

# ✅ 수정: FastAPI 앱 테스트 클라이언트 (httpx 0.28+ 호환)
@pytest_asyncio.fixture
async def async_client(db_session):
    """
    FastAPI 앱을 테스트하기 위한 AsyncClient.
    Dependency Override를 통해 테스트용 DB 세션을 사용하도록 강제합니다.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # ASGITransport 사용 (httpx 최신 버전 권장 방식)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

# 테스트용 사용자 데이터
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """테스트용 사용자 생성"""
    stmt = select(User).where(User.github_user_id == 99999)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            github_user_id=99999,
            github_username="test_fixture_user",
            access_token_encrypted="gAAAA..."
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_user_token(test_user):
    """테스트 유저에 대한 유효한 JWT 토큰 발급"""
    # sub 필드에 user.id(UUID)를 문자열로 변환하여 저장
    return create_access_token(subject=str(test_user.id))