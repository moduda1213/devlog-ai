import calendar
from datetime import date as dateType, timedelta
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models import Journal
from app.schemas.stats import (
    WeeklyStatsResponse, MonthlyStatsResponse, 
    StatsDataset, DailyContribution
)

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_weekly_stats(self, user_id: UUID) -> WeeklyStatsResponse:
        """
        최근 7일간의 요일별 통계 조회
        1. 최근 7일 날짜 리스트 생성
        2. DB에서 해당 기간 데이터 group_by 조회
        3. 빈 날짜 0으로 채우기 및 포맷팅
        """
        today = dateType.today()
        start_date = today - timedelta(days=6)
        
        # 1. 최근 7일 날짜 리스트 생성(라벨용)
        date_range = [start_date + timedelta(days=i) for i in range(7)]
        labels = [d.strftime("%a") for d in date_range] # %a : 축약된 요일 이름입니다.
        
        # 2. DB 집계 쿼리
        stmt = (
            select(
                Journal.date,
                func.sum(Journal.commit_count).label("commits"),
                func.sum(Journal.files_changed).label("files")
            )
            .where(Journal.user_id == user_id, Journal.date >= start_date)
            .group_by(Journal.date)
        )
        result = await self.db.execute(stmt) # ex) result = [(Mon, 5), (Tue, 2), (Thu, 8)]
        stats_map = {row.date: row for row in result} # ex) {Mon: row1, Tue: row2, Thu: row3}
        
        # 3. 데이터셋 구성
        commit_data = [stats_map[d].commits if d in stats_map else 0 for d in date_range]
        file_data = [stats_map[d].files if d in stats_map else 0 for d in date_range]
        
        return WeeklyStatsResponse(
            labels=labels,
            datasets=[
                StatsDataset(label="Commits", data=commit_data),
                StatsDataset(label="Files Changed", data=file_data)
            ]
        )
        
    async def get_monthly_stats(self, user_id: UUID, year: int, month: int) -> MonthlyStatsResponse:
        """
        특정 월의 일별 활동 내역 및 요약 조회
        1. 해당 월의 시작일/종료일 계산
        2. DB 집계 (SUM, COUNT)
        3. 요약 정보 (평균 등) 계산
        """
        _, last_day = calendar.monthrange(year, month)
        start_date = dateType(year, month, 1)
        end_date = dateType(year, month, last_day)
        
        # 1. 월간 총합 데이터 집계
        summary_stmt = (
            select(
                func.sum(Journal.commit_count).label("total_commits"),
                func.count(Journal.id).label("total_journals")
            )
            .where(Journal.user_id == user_id, Journal.date.between(start_date, end_date))
        )
        summary_res = (await self.db.execute(summary_stmt)).one()
        total_commits = summary_res.total_commits or 0
        total_journals = summary_res.total_journals or 0
        
        # 2. 일별 상세 데이터 조회
        daily_stmt = (
            select(Journal.date, Journal.commit_count, Journal.id)
            .where(Journal.user_id == user_id, Journal.date.between(start_date, end_date))
        )
        daily_res = await self.db.execute(daily_stmt)
        daily_map = {row.date: row for row in daily_res}
        
        # 3. 전체 날짜 보정(잔디 심기용)
        contributions = []
        for i in range(1, last_day + 1):
            curr_date = dateType(year, month, i)
            if curr_date in daily_map:
                row = daily_map[curr_date]
                contributions.append(DailyContribution(
                    date=curr_date, count=row.commit_count, journal_id=str(row.id)
                ))
            else:
                contributions.append(DailyContribution(
                    date=curr_date, count=0, journal_id=None
                ))
                
        return MonthlyStatsResponse(
            year=year,
            month=month,
            total_commits=total_commits,
            total_journals=total_journals,
            daily_average=round(total_commits / last_day, 1),
            contributions=contributions
        )