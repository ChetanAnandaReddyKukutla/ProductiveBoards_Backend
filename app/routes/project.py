# app/routes/project.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import SessionLocal
from app.models.project import Project, project_members
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.project import ProjectCreate, ProjectOut
from app.core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    new_project = Project(title=project.title, description=project.description, owner_id=user["user_id"])
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Projects owned by the user OR where the user is a member
    projects = (
        db.query(Project)
        .outerjoin(project_members, Project.id == project_members.c.project_id)
        .filter(
            or_(
                Project.owner_id == user["user_id"],
                project_members.c.user_id == user["user_id"],
            )
        )
        .distinct()
        .all()
    )
    return projects

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Only owner or member can view
    if project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view project")
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, updated: ProjectCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    project.title = updated.title
    project.description = updated.description
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}

@router.post("/{project_id}/add-member/{user_id}")
def add_member(project_id: int, user_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only owner can add members")

    member = db.query(User).filter(User.id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")

    project.members.append(member)
    db.commit()
    return {"detail": f"{member.name} added as member"}

@router.post("/{project_id}/members/{user_id}")
def add_member_alt(project_id: int, user_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Alias of add_member, more RESTful path
    return add_member(project_id, user_id, db, user)

@router.get("/{project_id}/members", response_model=list[UserOut])
def list_members(project_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Owner or member can view
    if project.owner_id != user["user_id"] and all(m.id != user["user_id"] for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view members")
    return project.members

@router.delete("/{project_id}/members/{user_id}")
def remove_member(project_id: int, user_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Only owner can remove members")
    member = next((m for m in project.members if m.id == user_id), None)
    if not member:
        raise HTTPException(status_code=404, detail="User not a member of this project")
    project.members.remove(member)
    db.commit()
    return {"detail": f"{member.name} removed"}
