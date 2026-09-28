from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import InterviewType
from .common import ORMBaseSchema


class InterviewSessionCreate(BaseModel):
    student_id: int = Field(gt=0)
    career_id: int | None = Field(default=None, gt=0)
    session_type: InterviewType = InterviewType.GENERAL


class InterviewSessionResponse(ORMBaseSchema):
    id: int
    student_id: int
    career_id: int | None
    session_type: InterviewType
    overall_score: float | None
    feedback: str | None
    started_at: datetime
    completed_at: datetime | None


class InterviewAnswerCreate(BaseModel):
    session_id: int = Field(gt=0)
    question: str = Field(min_length=1)
    answer: str | None = None


class InterviewAnswerResponse(ORMBaseSchema):
    id: int
    session_id: int
    question: str
    answer: str | None
    feedback: str | None
    score: float | None
    created_at: datetime
