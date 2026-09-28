from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.dependencies import ensure_student_owner, get_own_student_profile
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.skill import SkillResponse
from backend.schemas.resume import ResumeResponse
from backend.services.resume_service import (
    create_resume,
    generate_resume_improvement,
    get_resume,
    list_resumes,
    process_resume,
    resolve_file_type,
    save_upload,
    sync_skills_from_resume,
)

router = APIRouter(prefix="/resumes", tags=["resume"])


class ImprovementRequest(BaseModel):
    target_career: str | None = None


class ImprovementResponse(BaseModel):
    improvement: str


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    profile: StudentProfile = Depends(get_own_student_profile),
    db: Session = Depends(get_db),
):
    try:
        file_type = resolve_file_type(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    file_path, file_name = save_upload(file, profile.id, file_type)
    resume = create_resume(db, profile.id, file_name, file_path, file_type)
    resume = process_resume(db, resume)
    sync_skills_from_resume(db, resume)
    return resume


@router.get("/me", response_model=list[ResumeResponse])
def list_my_resumes(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return list_resumes(db, profile.id)


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_one(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    ensure_student_owner(resume.student_id, current_user, db)
    return resume


@router.post("/{resume_id}/improve", response_model=ImprovementResponse)
def improve(
    resume_id: int,
    data: ImprovementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    ensure_student_owner(resume.student_id, current_user, db)
    return ImprovementResponse(improvement=generate_resume_improvement(resume, data.target_career))


@router.post("/{resume_id}/sync-skills", response_model=list[SkillResponse])
def sync_skills(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    ensure_student_owner(resume.student_id, current_user, db)
    return sync_skills_from_resume(db, resume)
