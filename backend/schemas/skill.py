from datetime import datetime
from pydantic import BaseModel, Field
from backend.database.models.enums import ProficiencyLevel, SkillImportance, SkillSource
from .common import ORMBaseSchema


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None


class SkillResponse(ORMBaseSchema):
    id: int
    name: str
    category: str | None
    description: str | None
    created_at: datetime


class StudentSkillCreate(BaseModel):
    student_id: int = Field(gt=0)
    skill_id: int = Field(gt=0)
    proficiency_level: ProficiencyLevel
    source: SkillSource = SkillSource.PROFILE


class StudentSkillResponse(ORMBaseSchema):
    id: int
    student_id: int
    skill_id: int
    proficiency_level: ProficiencyLevel
    source: SkillSource
    created_at: datetime


class CareerSkillCreate(BaseModel):
    career_id: int = Field(gt=0)
    skill_id: int = Field(gt=0)
    importance: SkillImportance
    minimum_level: ProficiencyLevel


class CareerSkillResponse(ORMBaseSchema):
    id: int
    career_id: int
    skill_id: int
    importance: SkillImportance
    minimum_level: ProficiencyLevel
    created_at: datetime
