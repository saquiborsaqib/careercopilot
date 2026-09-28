from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import LearningLevel
from .common import ORMBaseSchema


class CertificationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    provider: str = Field(min_length=1, max_length=150)
    description: str | None = None
    url: str | None = Field(default=None, max_length=500)
    level: LearningLevel | None = None


class CertificationResponse(ORMBaseSchema):
    id: int
    name: str
    provider: str
    description: str | None
    url: str | None
    level: LearningLevel | None
    created_at: datetime
