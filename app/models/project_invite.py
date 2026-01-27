from enum import Enum as PyEnum
from datetime import datetime

from sqlalchemy import func, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvitationStatus(str, PyEnum):
    pending = 'pending'
    accepted = 'accepted'
    declined = 'declined'


class ProjectInvite(Base):
    __tablename__ = 'project_invites'

    __table_args__ = (
        UniqueConstraint(
            'project_id',
            'invited_user_id',
            name='uq_project_invite_project_user'
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )

    invited_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    invited_by_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus, name='invitation_status'),
        nullable=False,
        server_default=InvitationStatus.pending.value
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    project = relationship(
        'Project',
        back_populates='invites'
    )

    invited_user = relationship(
        'User',
        foreign_keys=[invited_user_id],
        back_populates='received_invites'
    )

    invited_by = relationship(
        'User',
        foreign_keys=[invited_by_id],
        back_populates='sent_invites'
    )
