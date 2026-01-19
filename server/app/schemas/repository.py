from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict, Field

# 1. GitHub API에서 받아오는 순수 데이터 구조
class GithubRepo(BaseModel):
    id: int  # GitHub의 Repository ID
    name: str
    full_name: str
    html_url: HttpUrl
    description: str | None = None
    private: bool
    # UI 편의를 위해 DB 상태와 병합될 필드
    is_selected: bool = False

# 2. 클라이언트가 저장소 선택 요청 시 보낼 데이터
class RepositorySelect(BaseModel):
    repo_name: str = Field(..., description="GitHub 저장소 전체 이름 (예: user/repo)")
    repo_url: str = Field(..., description="GitHub 저장소 URL") # HttpUrl 대신 str로 받아도 무방 (DB 저장용)

# 3. DB에 저장된 저장소 응답 (ORM 매핑용)
class RepositoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    repo_name: str
    repo_url: str
    is_selected: bool
    created_at: datetime

    # ORM 객체를 Pydantic 모델로 변환 허용
    model_config = ConfigDict(from_attributes=True)