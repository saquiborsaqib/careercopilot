from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from backend.database.models.enums import RecommendationType
from .common import ORMBaseSchema


class RecommendationCreate(BaseModel):
    student_id: int = Field(gt=0)
    recommendation_type: RecommendationType
    career_id: int | None = Field(default=None, gt=0)
    course_id: int | None = Field(default=None, gt=0)
    certification_id: int | None = Field(default=None, gt=0)
    opportunity_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=200)
    explanation: str | None = None
    score: float | None = Field(default=None, ge=0, le=100)
    source: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_target(self):
        mapping = {
            RecommendationType.CAREER: self.career_id,
            RecommendationType.COURSE: self.course_id,
            RecommendationType.CERTIFICATION: self.certification_id,
            RecommendationType.OPPORTUNITY: self.opportunity_id,
            RecommendationType.SKILL: None,
        }
        populated = sum(x is not None for x in [self.career_id, self.course_id, self.certification_id, self.opportunity_id])
        if self.recommendation_type == RecommendationType.SKILL:
            if populated:
                raise ValueError("SKILL recommendations must not contain a catalog target ID")
        elif mapping[self.recommendation_type] is None or populated != 1:
            raise ValueError("Exactly one target ID matching recommendation_type is required")
        return self


class RecommendationResponse(ORMBaseSchema):
    id: int
    student_id: int
    recommendation_type: RecommendationType
    career_id: int | None
    course_id: int | None
    certification_id: int | None
    opportunity_id: int | None
    title: str
    explanation: str | None
    score: float | None
    source: str | None
    created_at: datetime
