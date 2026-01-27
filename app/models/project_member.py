from enum import Enum as PyEnum
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class ProjectRole(str, PyEnum):
    owner = "owner"
    admin = "admin"
    member = "member"

class ProjectMember(Base):
    __tablename__ = "project_members"

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete='CASCADE'),
        primary_key=True
    )

    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name='project_role'),
        nullable=False,
        default=ProjectRole.member,
        server_default=ProjectRole.member.value
    )

    user = relationship("User", back_populates='project_members')
    project = relationship("Project", back_populates="members")