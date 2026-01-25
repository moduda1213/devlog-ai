from datetime import date as dateType
from pydantic import BaseModel, Field, ConfigDict

# -----------------------------------------------------------------------------
# Shared Components
# -----------------------------------------------------------------------------

class StatsDataset(BaseModel):
    """
    차트 데이터셋 스키마 (Chart.js 호환)
    예: { "label": "Commit Count", "data": [5, 2, 0, 8, ...] }
    """
    label: str = Field(..., description="데이터셋 라벨 (예: 커밋 수)")
    data: list[int] = Field(..., description="데이터 값 배열")

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Weekly Stats Schemas
# -----------------------------------------------------------------------------

class WeeklyStatsResponse(BaseModel):
    """
    주간 통계 응답 스키마
    
    최근 7일(또는 특정 주)의 데이터를 요일별로 집계하여 반환합니다.
    프론트엔드 차트 라이브러리에 바인딩하기 쉬운 구조입니다.
    """
    labels: list[str] = Field(
        ..., 
        description="X축 라벨 (날짜 또는 요일, 예: ['Mon', 'Tue', ...])"
    )
    datasets: list[StatsDataset] = Field(
        ..., 
        description="Y축 데이터셋 목록 (커밋 수, 일지 작성 수 등)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "datasets": [
                    {"label": "Commits", "data": [5, 2, 8, 1, 0, 0, 3]},
                    {"label": "Journals", "data": [1, 1, 1, 1, 0, 0, 1]}
                ]
            }
        }
    )


# -----------------------------------------------------------------------------
# Monthly Stats Schemas
# -----------------------------------------------------------------------------

class DailyContribution(BaseModel):
    """일별 활동량 (GitHub 잔디 심기 UI용)"""
    date: dateType = Field(..., description="날짜 (YYYY-MM-DD)")
    count: int = Field(..., description="활동 수 (커밋 수)", ge=0)
    journal_id: str | None = Field(None, description="해당 날짜의 일지 ID (있을 경우)")

    model_config = ConfigDict(from_attributes=True)


class MonthlyStatsResponse(BaseModel):
    """
    월간 통계 응답 스키마

    해당 월의 전체 활동 내역과 요약 정보를 반환합니다.
    """
    year: int = Field(..., description="조회 연도")
    month: int = Field(..., description="조회 월")

    # 요약 메트릭
    total_commits: int = Field(..., description="월간 총 커밋 수", ge=0)
    total_journals: int = Field(..., description="월간 총 일지 수", ge=0)
    daily_average: float = Field(..., description="일평균 커밋 수", ge=0.0)

    # 상세 데이터 (잔디 심기용)
    contributions: list[DailyContribution] = Field(..., description="일별 활동 내역")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "year": 2026,
                "month": 1,
                "total_commits": 150,
                "total_journals": 20,
                "daily_average": 4.8,
                "contributions": [
                    {"date": "2026-01-01", "count": 5, "journal_id": "uuid..."},
                    {"date": "2026-01-02", "count": 3, "journal_id": None}
                ]
            }
        }
    )