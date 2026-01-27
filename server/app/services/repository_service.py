from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.repository import Repository
from app.schemas.repository import GithubRepo

async def get_merged_repositories(
    user_id: UUID, 
    github_repos: list[dict], 
    db: AsyncSession
) -> list[GithubRepo]:
    """GitHub API 결과와 DB의 선택 상태를 병합하여 반환"""
    
    # 1. DB에서 현재 선택된 저장소 조회
    stmt = select(Repository).where(
        Repository.user_id == user_id,
        Repository.is_selected
    )
    result = await db.execute(stmt)
    selected_repo = result.scalar_one_or_none()
    
    # 2. 병합 로직
    response_data = []
    
    for repo in github_repos:
        is_selected = False
        
        if selected_repo and repo["full_name"] == selected_repo.repo_name:
            is_selected = True
            
        response_data.append(GithubRepo(
            id=repo["id"],
            name=repo["name"],
            full_name=repo["full_name"],
            html_url=repo["html_url"],
            description=repo["description"],
            private=repo["private"],
            is_selected=is_selected
        ))
        
    return response_data

async def select_repository(
    user_id: UUID,
    repo_name: str,
    repo_url: str,
    db: AsyncSession
) -> Repository:
    """ 저장소 선택 (R-BIZ-1: 단일 저장소 선택) """
    try:
        # 1. 기존 선택 모두 해제
        await db.execute(
            update(Repository)
            .where(Repository.user_id == user_id)
            .values(is_selected=False)
        )

        # 2. 저장소 조회 (Upsert 로직)
        stmt = select(Repository).where(
            Repository.user_id == user_id,
            Repository.repo_name == repo_name
        )

        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()

        if repo:
            repo.is_selected = True
            repo.repo_url = repo_url
            db.add(repo)

        else:
            repo = Repository(
                user_id=user_id,
                repo_name=repo_name,
                repo_url=repo_url,
                is_selected=True
            )

            db.add(repo)

        await db.commit()
        await db.refresh(repo)
        return repo

    except Exception as e:
        await db.rollback()
        raise e