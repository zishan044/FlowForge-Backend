from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus | None = TaskStatus.todo
    project_id: int
    assignee_id: int | None = None

class TaskRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime
