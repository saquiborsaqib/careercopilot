from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User


def get_own_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentProfile:
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create a student profile before using this feature",
        )
    return profile


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def ensure_student_owner(student_id: int, current_user: User, db: Session) -> StudentProfile:
    profile = db.get(StudentProfile, student_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    if profile.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this student profile")
    return profile
