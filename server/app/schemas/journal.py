from uuid import UUID
from datetime import date as date_type, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class JournalBase(BaseModel):
    summary: str = Field(..., description="3문장 요약", max_length=500)
    main_tasks: list[str] = Field(..., description="주요 작업 목록")
    learned_things: list[str] = Field(..., description="배운 점 목록")
   
    # 통계 정보는 AI 생성 외에도 GitHub 데이터에서 직접 추출 가능
    commit_count: int = Field(0, ge=0)
    files_changed: int = Field(0, ge=0)
    lines_added: int = Field(0, ge=0)
    lines_deleted: int = Field(0, ge=0)
    
class JournalCreate(JournalBase):
    """일지 생성 시 필요한 데이터 (Service 내부용)"""
    user_id: UUID
    repository_id: UUID
    date: date_type
    raw_commits: list[dict[str, Any]] | None = None
    
class JournalUpdate(BaseModel):
    summary: str | None = None
    main_tasks: list[str] | None = None
    learned_things: list[str] | None = None
    
class JournalResponse(JournalBase):
    id: UUID
    user_id: UUID
    repository_id: UUID
    date: date_type
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class JournalListResponse(BaseModel):
    items: list[JournalResponse] = Field(..., description="현재 페이지의 일지 목록")
    total: int = Field(..., description="전체 일지 개수")
    page: int = Field(..., description="현재 페이지 번호")
    size: int = Field(..., description="페이지 크기")