from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import DemandLevel
from .common import ORMBaseSchema


class CareerCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=100)
    demand_level: DemandLevel | None = None


class CareerResponse(ORMBaseSchema):
    id: int
    title: str
    description: str | None
    industry: str | None
    demand_level: DemandLevel | None
    created_at: datetime
