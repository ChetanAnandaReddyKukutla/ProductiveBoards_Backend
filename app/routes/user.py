from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserOut
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Return basic user info for assignment dropdowns
    return db.query(User).all()
