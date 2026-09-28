from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import AnalysisStatus, ResumeFileType
from .common import ORMBaseSchema


class ResumeCreate(BaseModel):
    student_id: int = Field(gt=0)
    file_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_type: ResumeFileType


class ResumeResponse(ORMBaseSchema):
    id: int
    student_id: int
    file_name: str
    file_path: str
    file_type: ResumeFileType
    extracted_text: str | None
    analysis_status: AnalysisStatus
    uploaded_at: datetime
    updated_at: datetime
