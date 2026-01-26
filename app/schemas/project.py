from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True