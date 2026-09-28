from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_own_student_profile, require_admin
from backend.database.connection import get_db
from backend.database.models.enums import OpportunityType
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.opportunity import OpportunityCreate, OpportunityResponse
from backend.services.opportunity_service import (
    create_opportunity,
    get_opportunity,
    list_opportunities,
    match_opportunities_for_student,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityResponse])
def list_all(opportunity_type: OpportunityType | None = None, location: str | None = None, db: Session = Depends(get_db)):
    return list_opportunities(db, opportunity_type, location)


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create(data: OpportunityCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return create_opportunity(db, data)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_one(opportunity_id: int, db: Session = Depends(get_db)):
    opportunity = get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.get("/matches/me", response_model=list[OpportunityResponse])
def matches_for_me(
    opportunity_type: OpportunityType | None = None,
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    return match_opportunities_for_student(db, profile, opportunity_type)
