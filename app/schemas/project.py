from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.schemas.project_member import ProjectMemberRead
from app.schemas.project_invite import ProjectInviteRead
from app.schemas.task import TaskRead

class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    created_at: datetime
    tasks: list[TaskRead]
    members: list[ProjectMemberRead]
    invites: list[ProjectInviteRead]