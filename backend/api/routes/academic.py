from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import ensure_student_owner, get_own_student_profile
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.academic import AcademicRecordCreate, AcademicRecordResponse
from backend.services.academic_service import create_academic_record, delete_academic_record, get_academic_record, list_academic_records

router = APIRouter(prefix="/academic-records", tags=["academic"])


@router.get("/me", response_model=list[AcademicRecordResponse])
def list_my_academic_records(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return list_academic_records(db, profile.id)


@router.post("", response_model=AcademicRecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    data: AcademicRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_owner(data.student_id, current_user, db)
    return create_academic_record(db, data)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_academic_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Academic record not found")
    ensure_student_owner(record.student_id, current_user, db)
    delete_academic_record(db, record)
