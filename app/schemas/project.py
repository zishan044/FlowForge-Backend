from pydantic import BaseModel
from datetime import datetime

from app.schemas.project_member import ProjectMemberRead

class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime
    members: list[ProjectMemberRead]

    class Config:
        from_attributes = True