import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FK: User
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    repo_name: Mapped[str] = mapped_column(String(255)) # 예: "octocat/Hello-World"
    repo_url: Mapped[str] = mapped_column(String(500))
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 관계 정의
    user = relationship(
        "User", 
        back_populates="repositories",
        foreign_keys="[Repository.user_id]"
    )
    logs = relationship("DevLog", back_populates="repository")

    # 복합 유니크 제약 조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('user_id', 'repo_name', name='uq_user_repo'),
        Index('ix_repo_user_selected', 'user_id', 'is_selected'),
    )