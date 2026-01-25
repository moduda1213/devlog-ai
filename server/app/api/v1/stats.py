from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas.stats import WeeklyStatsResponse, MonthlyStatsResponse
from app.services.stats_service import StatsService

router = APIRouter()

@router.get("/weekly", response_model=WeeklyStatsResponse)
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    주간 통계 조회
    
    최근 7일간의 요일별 커밋 수와 파일 변경 수를 반환합니다.
    """
    service = StatsService(db)
    return await service.get_weekly_stats(current_user.id)

@router.get("/monthly", response_model=MonthlyStatsResponse)
async def get_monthly_stats(
    year: int | None = Query(None, description="조회 연도 (기본값: 현재 연도)"),
    month: int | None = Query(None, description="조회 월 (기본값: 현재 월)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    월간 통계 조회
    
    특정 월의 일별 활동 내역(잔디 심기용)과 요약 정보를 반환합니다.
    파라미터 생략 시 현재 연/월을 기준으로 조회합니다.
    """
    today = date.today()
    target_year = year if year else today.year
    target_month = month if month else today.month
    
    service = StatsService(db)
    return await service.get_monthly_stats(
        user_id=current_user.id,
        year=target_year,
        month=target_month
    )