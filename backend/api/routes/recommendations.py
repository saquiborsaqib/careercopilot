from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.dependencies import get_own_student_profile
from backend.database.connection import get_db
from backend.database.models.enums import RecommendationType
from backend.database.models.student import StudentProfile
from backend.schemas.recommendation import RecommendationResponse
from backend.services.recommendation_service import (
    generate_career_recommendations,
    generate_certification_recommendations,
    generate_course_recommendations,
    list_recommendations,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/me", response_model=list[RecommendationResponse])
def list_my_recommendations(
    recommendation_type: RecommendationType | None = None,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    return list_recommendations(db, profile.id, recommendation_type)


@router.post("/careers/generate", response_model=list[RecommendationResponse])
def generate_careers(
    top_n: int = 3,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    return generate_career_recommendations(db, profile, top_n)


@router.post("/courses/generate/{career_id}", response_model=list[RecommendationResponse])
def generate_courses(
    career_id: int,
    top_n: int = 5,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    try:
        return generate_course_recommendations(db, profile, career_id, top_n)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/certifications/generate/{career_id}", response_model=list[RecommendationResponse])
def generate_certifications(
    career_id: int,
    top_n: int = 3,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    try:
        return generate_certification_recommendations(db, profile, career_id, top_n)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
