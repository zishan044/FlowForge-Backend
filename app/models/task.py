from enum import Enum as PyEnum
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base

class TaskStatus(str, PyEnum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'

class Task(Base):
    __tablename__='tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name='task_status'),
        nullable=False,
        default=TaskStatus.todo,
        server_default=TaskStatus.todo.value,
    )


    project_id: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
    )

    assignee_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    project = relationship(
        'Project', 
        back_populates='tasks'
    )

    assignee = relationship(
        'User', 
        back_populates='tasks'
    )
