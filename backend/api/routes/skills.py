from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import ensure_student_owner, get_own_student_profile, require_admin
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.skill import SkillCreate, SkillResponse, StudentSkillCreate, StudentSkillResponse
from backend.services.skill_service import (
    create_skill,
    delete_student_skill,
    get_skill,
    list_skills,
    list_student_skills,
    upsert_student_skill,
)

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillResponse])
def list_catalog(category: str | None = None, db: Session = Depends(get_db)):
    return list_skills(db, category)


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_catalog_skill(data: SkillCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        return create_skill(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/me", response_model=list[StudentSkillResponse])
def list_my_skills(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return list_student_skills(db, profile.id)


@router.post("/assign", response_model=StudentSkillResponse, status_code=status.HTTP_201_CREATED)
def assign_skill(
    data: StudentSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_owner(data.student_id, current_user, db)
    if get_skill(db, data.skill_id) is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return upsert_student_skill(db, data)


@router.delete("/assign/{student_skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(
    student_skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.database.models.skill import StudentSkill

    row = db.get(StudentSkill, student_skill_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Student skill not found")
    ensure_student_owner(row.student_id, current_user, db)
    delete_student_skill(db, row)
