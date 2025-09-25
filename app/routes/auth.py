from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/signup",response_model=UserOut)
def signup(user:UserCreate, db: Session = Depends(get_db)):
    existingUser = db.query(User).filter(User.email == user.email).first()
    if(existingUser):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(form_data:UserLogin, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    token = create_access_token({"user_id":user.id, "email":user.email})
    return {"access_token":token, "token_type":"bearer"}