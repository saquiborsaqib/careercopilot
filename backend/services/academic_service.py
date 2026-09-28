from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.academic import AcademicRecord
from backend.schemas.academic import AcademicRecordCreate


def list_academic_records(db: Session, student_id: int) -> list[AcademicRecord]:
    return list(db.scalars(select(AcademicRecord).where(AcademicRecord.student_id == student_id)))


def create_academic_record(db: Session, data: AcademicRecordCreate) -> AcademicRecord:
    record = AcademicRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_academic_record(db: Session, record_id: int) -> AcademicRecord | None:
    return db.get(AcademicRecord, record_id)


def delete_academic_record(db: Session, record: AcademicRecord) -> None:
    db.delete(record)
    db.commit()
