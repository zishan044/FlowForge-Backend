from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.project_invite import InvitationStatus
from app.schemas.user import UserRead


class ProjectInviteCreate(BaseModel):
    invited_user_id: int


class ProjectInviteUpdate(BaseModel):
    status: InvitationStatus


class ProjectInviteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    invited_user_id: int
    invited_user: UserRead
    invited_by_id: int
    invited_by: UserRead
    status: InvitationStatus
    created_at: datetime
