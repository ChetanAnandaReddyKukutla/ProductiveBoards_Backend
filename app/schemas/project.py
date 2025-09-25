from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int

    class Config:
        orm_mode = True
