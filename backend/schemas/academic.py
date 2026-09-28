from datetime import datetime
from pydantic import BaseModel, Field
from .common import ORMBaseSchema


class AcademicRecordCreate(BaseModel):
    student_id: int = Field(gt=0)
    qualification: str = Field(min_length=1, max_length=100)
    institution: str = Field(min_length=1, max_length=200)
    field_of_study: str | None = Field(default=None, max_length=150)
    percentage_or_cgpa: float | None = Field(default=None, ge=0, le=100)
    start_year: int | None = Field(default=None, ge=1950, le=2100)
    end_year: int | None = Field(default=None, ge=1950, le=2100)


class AcademicRecordResponse(ORMBaseSchema):
    id: int
    student_id: int
    qualification: str
    institution: str
    field_of_study: str | None
    percentage_or_cgpa: float | None
    start_year: int | None
    end_year: int | None
    created_at: datetime
