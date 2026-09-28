from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_own_student_profile
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.student import StudentProfileCreate, StudentProfileResponse, StudentProfileUpdate
from backend.services.student_service import create_student_profile, get_student_profile, update_student_profile

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/profiles/me", response_model=StudentProfileResponse)
def get_my_profile(profile: StudentProfile = Depends(get_own_student_profile)):
    return profile


def ensure_profile_owner(student_id: int, current_user: User, db: Session):
    profile = get_student_profile(db, student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found")
    if profile.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="You do not have access to this student profile")
    return profile


@router.post("/profiles", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    data: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="You can only create a profile for your own account")
    existing = get_student_profile_by_user_id(db, data.user_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Student profile already exists")
    return create_student_profile(db, data)


def get_student_profile_by_user_id(db: Session, user_id: int):
    from sqlalchemy import select
    from backend.database.models.student import StudentProfile
    return db.scalar(select(StudentProfile).where(StudentProfile.user_id == user_id))


@router.get("/profiles/{student_id}", response_model=StudentProfileResponse)
def get_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ensure_profile_owner(student_id, current_user, db)


@router.patch("/profiles/{student_id}", response_model=StudentProfileResponse)
def update_profile(
    student_id: int,
    data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = ensure_profile_owner(student_id, current_user, db)
    return update_student_profile(db, profile, data)
