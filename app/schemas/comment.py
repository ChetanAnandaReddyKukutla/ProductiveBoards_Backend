from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True