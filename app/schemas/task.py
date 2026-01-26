from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str | None = 'todo'
    project_id: int
    assignee_id: int | None = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    project_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
