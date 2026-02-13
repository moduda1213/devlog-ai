from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from uuid import UUID

from app.api.deps import get_current_user, get_db, get_redis
from app.models.user import User
from app.schemas.journal import JournalResponse, JournalUpdate, JournalListResponse, JournalStatusResponse
from app.services.journal_service import JournalService

from loguru import logger

router = APIRouter()

@router.get("/daily-status", response_model=JournalStatusResponse)
async def check_daily_status(
    date: date_type | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """오늘 일지 생성 가능 여부 확인"""
    target_date = date or date_type.today()
    service = JournalService(db)
    return await service.check_daily_status(current_user, target_date)

@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
async def create_journal(
    date: date_type | None = None,
    overwrite: bool = Query(True, description="이미 존재할 경우 덮어쓰기 여부"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """오늘의 개발 일지 생성"""
    logger.info(f"[Journals APIRouter] ➡️ 오늘 일지 생성 진입: Today {date or date_type.today()}")
    
    target_date = date or date_type.today()
    service = JournalService(db)
    
    try:
        return await service.create_daily_journal(current_user, target_date, overwrite)
    
    except ValueError as e:
        # 서비스에서 발생한 비즈니스 에러를 HTTP 에러로 변환
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("", response_model=JournalListResponse)
async def read_journals(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    repository_id: UUID = Query(..., description="저장소 ID 필터"),
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    currnet_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """일지 목록 조회 (페이지네이션)"""
    logger.info(f"[Journals APIRouter] 일지 목록 조회 진입: {start_date} ~ {end_date}  |  page: {page} | Repo: {repository_id}")
    
    service = JournalService(db)
    
    items, total = await service.get_journals(
        user_id=currnet_user.id,
        page=page,
        size=size,
        start_date=start_date,
        end_date=end_date,
        repository_id=repository_id
    )
     
    return {
        'items': items,
        'total': total,
        'page': page,
        'size': size
    }
    
@router.get("/{journal_id}", response_model=JournalResponse)
async def read_journal(
    journal_id: UUID,
    currnet_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """일지 상세 조회"""
    logger.info("[Journals APIRouter] 📒일지 상세 조회 진입")
    service = JournalService(db, redis)
    journal = await service.get_journal_detail(
        user_id=currnet_user.id, 
        journal_id=journal_id
    )
    
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    return journal

@router.patch("/{journal_id}", response_model=JournalResponse)
async def update_journal(
    journal_id: UUID,
    journal_in: JournalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """일지 수정"""
    logger.info("[Journal APIRouter] 📒일지 수정 진입")
    service = JournalService(db, redis)
    try:
        return await service.update_journal(current_user.id, journal_id, journal_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal(
    journal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """일지 삭제"""
    logger.info("[Journal APIRouter] ❌일지 삭제 시작!!")
    service = JournalService(db, redis)
    try:
        await service.delete_journal(current_user.id, journal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))