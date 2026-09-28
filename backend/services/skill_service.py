from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models.skill import Skill, StudentSkill
from backend.schemas.skill import SkillCreate, StudentSkillCreate


def list_skills(db: Session, category: str | None = None) -> list[Skill]:
    stmt = select(Skill)
    if category:
        stmt = stmt.where(Skill.category == category)
    return list(db.scalars(stmt.order_by(Skill.name)))


def get_skill(db: Session, skill_id: int) -> Skill | None:
    return db.get(Skill, skill_id)


def get_skill_by_name(db: Session, name: str) -> Skill | None:
    return db.scalar(select(Skill).where(Skill.name == name.strip()))


def create_skill(db: Session, data: SkillCreate) -> Skill:
    skill = Skill(**data.model_dump())
    db.add(skill)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("A skill with this name already exists")
    db.refresh(skill)
    return skill


def get_or_create_skill(db: Session, name: str, category: str | None = None) -> Skill:
    existing = get_skill_by_name(db, name)
    if existing is not None:
        return existing
    skill = Skill(name=name.strip(), category=category)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def list_student_skills(db: Session, student_id: int) -> list[StudentSkill]:
    return list(db.scalars(select(StudentSkill).where(StudentSkill.student_id == student_id)))


def upsert_student_skill(db: Session, data: StudentSkillCreate) -> StudentSkill:
    existing = db.scalar(
        select(StudentSkill).where(
            StudentSkill.student_id == data.student_id,
            StudentSkill.skill_id == data.skill_id,
        )
    )
    if existing is not None:
        existing.proficiency_level = data.proficiency_level
        existing.source = data.source
        db.commit()
        db.refresh(existing)
        return existing
    student_skill = StudentSkill(**data.model_dump())
    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)
    return student_skill


def delete_student_skill(db: Session, student_skill: StudentSkill) -> None:
    db.delete(student_skill)
    db.commit()
