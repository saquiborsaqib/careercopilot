from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_own_student_profile
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.services.dashboard_service import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me")
def get_my_dashboard(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return build_dashboard(db, profile)
