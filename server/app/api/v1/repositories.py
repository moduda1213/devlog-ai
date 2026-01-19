from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.repository import GithubRepo, RepositorySelect, RepositoryResponse
from app.services.github_service import get_repositories as fetch_github_repos
from app.services import repository_service

router = APIRouter()

@router.get("", response_model=List[GithubRepo])
async def get_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기")
):
    """GitHub 저장소 목록 조회"""
    github_repos = await fetch_github_repos(
        access_token=current_user.decrypted_access_token,
        page=page,
        per_page=size
    )
    
    return await repository_service.get_merged_repositories(
        user_id=current_user.id,
        github_repos=github_repos,
        db=db
    )

@router.post("/select", response_model=RepositoryResponse)
async def select_repository(
    repo_data: RepositorySelect,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """저장소 선택"""
    return await repository_service.select_repository(
        user_id=current_user.id,
        repo_name=repo_data.repo_name,
        repo_url=repo_data.repo_url,
        db=db
    )