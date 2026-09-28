from sqlalchemy.orm import Session
from backend.database.models.student import StudentProfile
from backend.schemas.student import StudentProfileCreate, StudentProfileUpdate


def create_student_profile(db: Session, data: StudentProfileCreate) -> StudentProfile:
    profile = StudentProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_student_profile(db: Session, student_id: int) -> StudentProfile | None:
    return db.get(StudentProfile, student_id)


def update_student_profile(db: Session, profile: StudentProfile, data: StudentProfileUpdate) -> StudentProfile:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
