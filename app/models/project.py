from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Project(Base):
    __tablename__="projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    whiteboard_id: Mapped[int] = mapped_column(
        ForeignKey("whiteboards.id", ondelete='CASCADE'),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    owner = relationship(
        'User',
        back_populates='owned_projects',
    )

    members = relationship(
        'ProjectMember',  
        back_populates='project',
        cascade='all, delete-orphan'
    )

    invites = relationship(
        'ProjectInvite',
        back_populates='project',
        cascade='all, delete-orphan'
    )

    tasks = relationship(
        "Task",
        back_populates='project',
        cascade='all, delete-orphan'
    )

    whiteboard = relationship(
        'WhiteBoard',
        back_populates='project',
        cascade='all, delete-orphan'
    )