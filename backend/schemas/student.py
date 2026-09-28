from datetime import datetime
from pydantic import BaseModel, Field
from .common import ORMBaseSchema


class StudentProfileCreate(BaseModel):
    user_id: int = Field(gt=0)
    college: str | None = Field(default=None, max_length=200)
    degree: str | None = Field(default=None, max_length=150)
    branch: str | None = Field(default=None, max_length=150)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    semester: int | None = Field(default=None, ge=1, le=20)
    cgpa: float | None = Field(default=None, ge=0, le=10)
    location: str | None = Field(default=None, max_length=150)
    career_interest: str | None = Field(default=None, max_length=200)
    preferred_location: str | None = Field(default=None, max_length=150)


class StudentProfileUpdate(BaseModel):
    college: str | None = Field(default=None, max_length=200)
    degree: str | None = Field(default=None, max_length=150)
    branch: str | None = Field(default=None, max_length=150)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    semester: int | None = Field(default=None, ge=1, le=20)
    cgpa: float | None = Field(default=None, ge=0, le=10)
    location: str | None = Field(default=None, max_length=150)
    career_interest: str | None = Field(default=None, max_length=200)
    preferred_location: str | None = Field(default=None, max_length=150)


class StudentProfileResponse(ORMBaseSchema):
    id: int
    user_id: int
    college: str | None
    degree: str | None
    branch: str | None
    graduation_year: int | None
    semester: int | None
    cgpa: float | None
    location: str | None
    career_interest: str | None
    preferred_location: str | None
    created_at: datetime
    updated_at: datetime
