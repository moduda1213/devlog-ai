import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.repository import Repository

@pytest.mark.asyncio
async def test_create_repository(db_session):
    """Repository 생성 및 User와의 관계 테스트"""
    # 1. User 생성
    user = User(
        github_username="repo_owner",
        github_user_id=1001,
        access_token_encrypted="token"
    )
    db_session.add(user)
    await db_session.commit()
    
    # 2. Repository 생성
    repo = Repository(
        user_id=user.id,
        repo_name="owner/awesome-project",
        repo_url="https://github.com/owner/awesome-project"
    )
    db_session.add(repo)
    await db_session.commit()
    
    # 3. 조회 및 검증
    await db_session.refresh(repo)
    assert repo.id is not None
    assert repo.user_id == user.id
    assert repo.is_selected is False  # default check

    # 4. 역방향 관계(User.repositories) 확인
    # (주의: async session에서는 relationship 로딩 시 전략 필요하지만, 여기선 FK 확인만으로 충분)
    stmt = select(Repository).where(Repository.user_id == user.id)
    result = await db_session.execute(stmt)
    repos = result.scalars().all()
    assert len(repos) == 1
    assert repos[0].repo_name == "owner/awesome-project"

@pytest.mark.asyncio
async def test_repository_unique_constraint(db_session):
    """Repository 중복 등록(같은 유저, 같은 저장소명) 방지 테스트"""
    # 1. User 생성
    user = User(
        github_username="uniq_tester",
        github_user_id=2002,
        access_token_encrypted="token"
    )
    db_session.add(user)
    await db_session.commit()

    # 2. 첫 번째 저장소 등록
    repo1 = Repository(
        user_id=user.id,
        repo_name="my/duplicate-repo",
        repo_url="https://github.com/my/duplicate-repo"
    )
    db_session.add(repo1)
    await db_session.commit()

    # 3. 같은 이름의 저장소 중복 등록 시도
    repo2 = Repository(
        user_id=user.id,
        repo_name="my/duplicate-repo",  # 중복!
        repo_url="https://github.com/my/duplicate-repo"
    )
    db_session.add(repo2)

    # 4. IntegrityError 발생 확인
    with pytest.raises(IntegrityError):
        await db_session.commit()
    
    await db_session.rollback()
