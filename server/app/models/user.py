import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.security import decrypt_token

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    # PK: UUID 자동 생성
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # GitHub 정보 (Unique)
    github_username: Mapped[str] = mapped_column(String(100), unique=True)
    github_user_id: Mapped[int] = mapped_column(Integer, unique=True)
    
    # 보안 정보 (암호화된 토큰)
    access_token_encrypted: Mapped[str] = mapped_column(String(500))
    
    # 선택된 저장소 (User 1 : Repository 1 관계 - MVP)
    # 순환 참조 방지를 위해 문자열로 클래스 명시 추천
    # use_alter=True: Circular Dependency 해결 (테이블 생성 후 제약조건 추가)
    selected_repo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("repositories.id", use_alter=True, name="fk_user_selected_repo")
    )

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계 정의 (문자열 참조 사용)
    repositories = relationship(
        "Repository", 
        back_populates="user", 
        cascade="all, delete-orphan",
        foreign_keys="[Repository.user_id]"
    )
    logs = relationship("DevLog", back_populates="user")
    
    @property
    def decrypted_access_token(self) -> str:
        """암호화된 토큰을 복호화하여 반환"""
        if not self.access_token_encrypted:
            return ""
        try:
            return decrypt_token(self.access_token_encrypted)
        except Exception:
            # 복호화 실패 시 빈 문자열 반환 (또는 로깅)
            return ""