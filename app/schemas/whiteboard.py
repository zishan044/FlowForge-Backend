from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class WhiteBoardCreate(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)

class WhiteBoardUpdate(BaseModel):
    data: dict[str, Any]

class WhiteBoardRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: int
    project_id: int
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime