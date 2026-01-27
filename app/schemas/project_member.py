from pydantic import BaseModel
from app.models.project_member import ProjectRole
from app.schemas.user import UserRead


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: ProjectRole


class ProjectMemberRead(BaseModel):
    user_id: int
    user_info: UserRead
    role: ProjectRole

    model_config = { "from_attributes": True }
