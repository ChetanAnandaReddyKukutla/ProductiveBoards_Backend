from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.comment import Comment
from app.models.task import Task
from app.core.security import get_current_user
from app.schemas.comment import CommentCreate, CommentOut
from typing import List

router = APIRouter(prefix="/comments", tags=["Comments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/task/{task_id}", response_model=CommentOut)
def add_comment(task_id: int, comment: CommentCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Only owner or project members may comment
    if task.project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in task.project.members):
        raise HTTPException(status_code=403, detail="Not authorized to comment on this task")

    new_comment = Comment(
        content=comment.content,
        task_id=task_id,
        user_id=user["user_id"]
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/task/{task_id}", response_model=List[CommentOut])
def get_comments(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in task.project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view comments for this task")
    comments = db.query(Comment).filter(Comment.task_id == task_id).all()
    return comments