from pydantic import BaseModel, ConfigDict
from app.models.project_member import ProjectRole
from app.schemas.user import UserRead


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: ProjectRole


class ProjectMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    user: UserRead
    role: ProjectRole
