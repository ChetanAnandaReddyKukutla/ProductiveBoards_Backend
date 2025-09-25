# app/routes/task.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.task import Task,TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.core.security import get_current_user
from app.models.project import Project

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/project/{project_id}", response_model=TaskOut)
def create_task(project_id: int, task: TaskCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to add tasks")

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=project_id,
        assignee_id=task.assignee_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updated: TaskUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update task")

    if 'title' in updated.model_fields_set:
        task.title = updated.title
    if 'description' in updated.model_fields_set:
        task.description = updated.description
    if 'status' in updated.model_fields_set:
        task.status = updated.status
    if 'priority' in updated.model_fields_set:
        task.priority = updated.priority
    if 'assignee_id' in updated.model_fields_set:
        task.assignee_id = updated.assignee_id
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete task")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

@router.get("/project/{project_id}", response_model=list[TaskOut])
def list_tasks(
    project_id: int,
    status: TaskStatus | None = Query(None),
    priority: TaskPriority | None = Query(None),
    assignee_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    # Authorization: only owner or project member may view tasks
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view tasks for this project")

    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    return query.all()

# Quick status actions
@router.patch("/{task_id}/in-progress", response_model=TaskOut)
def mark_in_progress(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Allow owner or project members to move status
    if task.project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in task.project.members):
        raise HTTPException(status_code=403, detail="Not authorized to update task status")
    task.status = TaskStatus.in_progress
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}/done", response_model=TaskOut)
def mark_done(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in task.project.members):
        raise HTTPException(status_code=403, detail="Not authorized to update task status")
    task.status = TaskStatus.done
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}/todo", response_model=TaskOut)
def mark_todo(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in task.project.members):
        raise HTTPException(status_code=403, detail="Not authorized to update task status")
    task.status = TaskStatus.todo
    db.commit()
    db.refresh(task)
    return task
