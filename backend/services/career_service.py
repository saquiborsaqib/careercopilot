from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend.database.models.career import Career
from backend.database.models.skill import CareerSkill
from backend.schemas.career import CareerCreate
from backend.schemas.skill import CareerSkillCreate


def list_careers(db: Session, industry: str | None = None) -> list[Career]:
    stmt = select(Career)
    if industry:
        stmt = stmt.where(Career.industry == industry)
    return list(db.scalars(stmt.order_by(Career.title)))


def get_career(db: Session, career_id: int) -> Career | None:
    return db.get(Career, career_id)


def get_career_by_title(db: Session, title: str) -> Career | None:
    return db.scalar(select(Career).where(Career.title == title.strip()))


def create_career(db: Session, data: CareerCreate) -> Career:
    career = Career(**data.model_dump())
    db.add(career)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("A career with this title already exists")
    db.refresh(career)
    return career


def list_career_skills(db: Session, career_id: int) -> list[CareerSkill]:
    stmt = (
        select(CareerSkill)
        .where(CareerSkill.career_id == career_id)
        .options(selectinload(CareerSkill.skill))
    )
    return list(db.scalars(stmt))


def add_career_skill(db: Session, data: CareerSkillCreate) -> CareerSkill:
    existing = db.scalar(
        select(CareerSkill).where(
            CareerSkill.career_id == data.career_id,
            CareerSkill.skill_id == data.skill_id,
        )
    )
    if existing is not None:
        existing.importance = data.importance
        existing.minimum_level = data.minimum_level
        db.commit()
        db.refresh(existing)
        return existing
    career_skill = CareerSkill(**data.model_dump())
    db.add(career_skill)
    db.commit()
    db.refresh(career_skill)
    return career_skill
