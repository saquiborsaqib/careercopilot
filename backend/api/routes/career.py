from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_own_student_profile, require_admin
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.career import CareerCreate, CareerResponse
from backend.schemas.skill import CareerSkillCreate, CareerSkillResponse
from backend.services.career_engine_service import compute_skill_gap, recommend_careers
from backend.services.career_service import add_career_skill, create_career, get_career, list_career_skills, list_careers

router = APIRouter(prefix="/careers", tags=["career"])


@router.get("", response_model=list[CareerResponse])
def list_catalog(industry: str | None = None, db: Session = Depends(get_db)):
    return list_careers(db, industry)


@router.post("", response_model=CareerResponse, status_code=status.HTTP_201_CREATED)
def create_catalog_career(data: CareerCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        return create_career(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/{career_id}", response_model=CareerResponse)
def get_catalog_career(career_id: int, db: Session = Depends(get_db)):
    career = get_career(db, career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")
    return career


@router.get("/{career_id}/skills", response_model=list[CareerSkillResponse])
def get_career_skills(career_id: int, db: Session = Depends(get_db)):
    return list_career_skills(db, career_id)


@router.post("/{career_id}/skills", response_model=CareerSkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill_to_career(career_id: int, data: CareerSkillCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if career_id != data.career_id:
        raise HTTPException(status_code=400, detail="career_id in path and body must match")
    return add_career_skill(db, data)


@router.get("/{career_id}/skill-gap")
def get_skill_gap(
    career_id: int,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    try:
        report = compute_skill_gap(db, profile.id, career_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return asdict(report)


@router.get("/recommendations/me")
def get_career_recommendations(
    top_n: int = 5,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    matches = recommend_careers(db, profile, top_n=top_n)
    return [
        {
            "career": CareerResponse.model_validate(match.career).model_dump(),
            "overall_score": match.overall_score,
            "skill_match_score": match.skill_match_score,
            "semantic_score": match.semantic_score,
            "matched_skill_count": match.matched_skill_count,
            "required_skill_count": match.required_skill_count,
        }
        for match in matches
    ]
