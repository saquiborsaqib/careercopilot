from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from backend.database.models.enums import UserRole
from .common import ORMBaseSchema


class UserCreate(BaseModel):
    """Public self-registration payload. There is deliberately no `role`
    field here: every self-registered account is a student. Admin accounts
    are provisioned out-of-band via backend.scripts.create_admin, never
    through this open endpoint."""

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(ORMBaseSchema):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
