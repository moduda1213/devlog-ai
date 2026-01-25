import pytest_asyncio
import fakeredis.aioredis

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import date
from uuid import uuid4

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models import User, Repository, Journal
from app.main import app

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

@pytest_asyncio.fixture
async def mock_redis():
    """테스트용 In-Memory Redis"""
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.close()
   
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
async def test_journal(db_session: AsyncSession, test_user: User, test_repo: Repository) -> Journal:
    """테스트용 일지 생성 (Get or Create 패턴 적용)"""
    # 1. 먼저 DB에 존재하는지 확인
    stmt = select(Journal).where(
        Journal.user_id == test_user.id,
        Journal.repository_id == test_repo.id,
        Journal.date == date.today()
    )
    result = await db_session.execute(stmt)
    journal = result.scalar_one_or_none()
    
    # 2. 없으면 새로 생성
    if not journal:
        journal = Journal(
            user_id=test_user.id,
            repository_id=test_repo.id,
            date=date.today(),
            summary="Test Summary",
            main_tasks=["Task 1", "Task 2"],
            learned_things=["Thing 1"],
            commit_count=5
        )
        db_session.add(journal)
        await db_session.commit()
        await db_session.refresh(journal)
    
    return journal

@pytest_asyncio.fixture
async def test_user_token(test_user):
    """테스트 유저에 대한 유효한 JWT 토큰 발급"""
    # sub 필드에 user.id(UUID)를 문자열로 변환하여 저장
    return create_access_token(subject=str(test_user.id))

@pytest_asyncio.fixture
async def access_token_header(test_user_token):
    """API 요청용 인증 헤더"""
    return {"Authorization": f"Bearer {test_user_token}"}

@pytest_asyncio.fixture
async def test_repo(db_session: AsyncSession, test_user: User):
    """
    test_user에게 연결된 선택된 저장소 생성
    (일지 생성 테스트를 위한 전제 조건)
    """
    # 중복 확인: 이미 'test/repo'가 있는지 조회
    stmt = select(Repository).where(
        Repository.user_id == test_user.id,
        Repository.repo_name == "test/repo"
    )
    result = await db_session.execute(stmt)
    repo = result.scalar_one_or_none()
    
    # 1. 저장소 생성
    if not repo:
        repo = Repository(
            id=uuid4(),
            user_id=test_user.id,
            repo_name="test/repo",
            repo_url="https://github.com/test/repo",
            is_selected=True
        )
        
        db_session.add(repo)
        # User의 selected_repo_id 업데이트
        test_user.selected_repo_id = repo.id
        db_session.add(test_user) # User 업데이트 명시
        
        await db_session.commit()
        await db_session.refresh(repo)
    
    return repo

############################################################################
#            제 2의 사용자 테스터                                             #
############################################################################  
@pytest_asyncio.fixture
async def test_other_user(db_session: AsyncSession):
    """테스트용 제2 사용자 (타인) 생성"""
    stmt = select(User).where(User.github_user_id == 88888)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            github_user_id=88888,
            github_username="other_user",
            access_token_encrypted="gAAAA_other..."
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_other_user_token(test_other_user):
    """제2 사용자의 토큰"""
    return create_access_token(subject=str(test_other_user.id))