from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    owned_projects = relationship(
        'Project',
        back_populates='owner',
        cascade='all, delete-orphan'
    )

    project_members = relationship(
        'ProjectMember',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    sent_invites = relationship(
        'ProjectInvite',
        back_populates='invited_by',
        cascade='all, delete-orphan',
        foreign_keys='ProjectInvite.invited_by_id'
    )

    received_invites = relationship(
        'ProjectInvite',
        back_populates='invited_user',
        cascade='all, delete-orphan',
        foreign_keys='ProjectInvite.invited_user_id'
    )

    tasks = relationship(
        "Task",
        back_populates='assignee',
        cascade="all, delete-orphan"
    )
