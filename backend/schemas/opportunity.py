from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import OpportunityType
from .common import ORMBaseSchema


class OpportunityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    organization: str = Field(min_length=1, max_length=200)
    opportunity_type: OpportunityType
    description: str | None = None
    location: str | None = Field(default=None, max_length=150)
    eligibility: str | None = None
    application_url: str | None = Field(default=None, max_length=500)
    deadline: datetime | None = None
    source: str | None = Field(default=None, max_length=200)


class OpportunityResponse(ORMBaseSchema):
    id: int
    title: str
    organization: str
    opportunity_type: OpportunityType
    description: str | None
    location: str | None
    eligibility: str | None
    application_url: str | None
    deadline: datetime | None
    source: str | None
    created_at: datetime
