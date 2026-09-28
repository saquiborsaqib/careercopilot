from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import RoadmapItemStatus, RoadmapStatus
from .common import ORMBaseSchema


class RoadmapCreate(BaseModel):
    student_id: int = Field(gt=0)
    career_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class RoadmapItemCreate(BaseModel):
    roadmap_id: int = Field(gt=0)
    skill_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    sequence: int = Field(ge=1)
    status: RoadmapItemStatus = RoadmapItemStatus.NOT_STARTED


class RoadmapItemResponse(ORMBaseSchema):
    id: int
    roadmap_id: int
    skill_id: int | None
    title: str
    description: str | None
    sequence: int
    status: RoadmapItemStatus
    created_at: datetime


class RoadmapResponse(ORMBaseSchema):
    id: int
    student_id: int
    career_id: int
    title: str
    description: str | None
    status: RoadmapStatus
    created_at: datetime
    updated_at: datetime
    items: list[RoadmapItemResponse] = Field(default_factory=list)
