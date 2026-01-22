import uuid
from datetime import date as dateType, datetime
from typing import Any

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FKs
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"))
    
    # Core Data
    date: Mapped[dateType] = mapped_column(Date, index=True)
    summary: Mapped[str] = mapped_column(String(500))
    
    # JSON Fields
    main_tasks: Mapped[list[str]] = mapped_column(JSON)
    learned_things: Mapped[list[str]] = mapped_column(JSON)
    
    # Statistics
    commit_count: Mapped[int] = mapped_column(Integer, default=0)
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    lines_added: Mapped[int] = mapped_column(Integer, default=0)
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0)
    
    # Debug Data (Nullable)
    raw_commits: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="journals")
    repository = relationship("Repository", back_populates="journals")

    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'repository_id', 'date', name='uq_user_repo_date'),
        Index('ix_user_date', 'user_id', 'date'),
    )
