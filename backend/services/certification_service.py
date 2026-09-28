from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models.certification import Certification
from backend.schemas.certification import CertificationCreate


def list_certifications(db: Session, level: str | None = None) -> list[Certification]:
    stmt = select(Certification)
    if level:
        stmt = stmt.where(Certification.level == level)
    return list(db.scalars(stmt.order_by(Certification.name)))


def get_certification(db: Session, certification_id: int) -> Certification | None:
    return db.get(Certification, certification_id)


def create_certification(db: Session, data: CertificationCreate) -> Certification:
    certification = Certification(**data.model_dump())
    db.add(certification)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("A certification with this name and provider already exists")
    db.refresh(certification)
    return certification
