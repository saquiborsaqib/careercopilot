from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import LearningLevel, PriceType
from .common import ORMBaseSchema


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    provider: str = Field(min_length=1, max_length=150)
    description: str | None = None
    url: str | None = Field(default=None, max_length=500)
    level: LearningLevel | None = None
    duration: str | None = Field(default=None, max_length=100)
    price_type: PriceType = PriceType.UNKNOWN


class CourseResponse(ORMBaseSchema):
    id: int
    title: str
    provider: str
    description: str | None
    url: str | None
    level: LearningLevel | None
    duration: str | None
    price_type: PriceType
    created_at: datetime
