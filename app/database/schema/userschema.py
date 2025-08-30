from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_superuser: bool


class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True  # Pydantic v2 / SQLAlchemy compat

class Token(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # email
    exp: int
