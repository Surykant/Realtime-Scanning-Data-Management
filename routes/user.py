from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schema.userschema import UserOut
from app.services.auth import get_current_user, require_superuser
from app.database.models.users import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/userdetail", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/allusers", response_model=list[UserOut])
def list_users(_: User = Depends(require_superuser), db: Session = Depends(get_db)):
    return db.query(User).all()
