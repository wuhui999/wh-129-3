from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
from schemas import UserOut

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("", response_model=list[UserOut])
def list_users(role: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    return q.all()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
