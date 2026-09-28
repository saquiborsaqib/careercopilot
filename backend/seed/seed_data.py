"""Idempotent seed loader for the catalog entities: skills, careers,
career-skill requirements, courses, certifications and opportunities.

Run with: python -m backend.seed.seed_data
Safe to re-run: existing rows (matched by unique name/title) are left as-is.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from backend.database.base import Base
from backend.database.connection import SessionLocal, engine
from backend.database.models.career import Career
from backend.database.models.certification import Certification
from backend.database.models.course import Course
from backend.database.models.opportunity import Opportunity
from backend.database.models.skill import CareerSkill, Skill
from backend.schemas.career import CareerCreate
from backend.schemas.certification import CertificationCreate
from backend.schemas.course import CourseCreate
from backend.schemas.opportunity import OpportunityCreate
from backend.schemas.skill import CareerSkillCreate, SkillCreate
from backend.services.career_service import add_career_skill, create_career, get_career_by_title
from backend.services.certification_service import create_certification
from backend.services.course_service import create_course
from backend.services.opportunity_service import create_opportunity
from backend.services.skill_service import create_skill, get_skill_by_name

SEED_DIR = Path(__file__).parent


def _load(filename: str) -> list[dict]:
    with open(SEED_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def seed_skills(db) -> dict[str, Skill]:
    skills_data = _load("skills.json")
    created, skipped = 0, 0
    for entry in skills_data:
        if get_skill_by_name(db, entry["name"]) is not None:
            skipped += 1
            continue
        create_skill(db, SkillCreate(**entry))
        created += 1
    print(f"Skills: {created} created, {skipped} already existed")
    return {row.name: row for row in db.query(Skill).all()}


def seed_careers(db, skills_by_name: dict[str, Skill]) -> None:
    careers_data = _load("careers.json")
    careers_created, careers_skipped = 0, 0
    links_created = 0

    for entry in careers_data:
        career = get_career_by_title(db, entry["title"])
        if career is None:
            career = create_career(
                db,
                CareerCreate(
                    title=entry["title"],
                    description=entry.get("description"),
                    industry=entry.get("industry"),
                    demand_level=entry.get("demand_level"),
                ),
            )
            careers_created += 1
        else:
            careers_skipped += 1

        for skill_req in entry.get("skills", []):
            skill = skills_by_name.get(skill_req["name"])
            if skill is None:
                continue
            existing = (
                db.query(CareerSkill)
                .filter(CareerSkill.career_id == career.id, CareerSkill.skill_id == skill.id)
                .first()
            )
            if existing is not None:
                continue
            add_career_skill(
                db,
                CareerSkillCreate(
                    career_id=career.id,
                    skill_id=skill.id,
                    importance=skill_req["importance"],
                    minimum_level=skill_req["minimum_level"],
                ),
            )
            links_created += 1

    print(f"Careers: {careers_created} created, {careers_skipped} already existed, {links_created} career-skill links created")


def seed_courses(db) -> None:
    courses_data = _load("courses.json")
    existing_titles = {row.title for row in db.query(Course).all()}
    created = 0
    for entry in courses_data:
        if entry["title"] in existing_titles:
            continue
        create_course(db, CourseCreate(**entry))
        created += 1
    print(f"Courses: {created} created, {len(courses_data) - created} already existed")


def seed_certifications(db) -> None:
    certs_data = _load("certifications.json")
    existing = {(row.name, row.provider) for row in db.query(Certification).all()}
    created = 0
    for entry in certs_data:
        if (entry["name"], entry["provider"]) in existing:
            continue
        create_certification(db, CertificationCreate(**entry))
        created += 1
    print(f"Certifications: {created} created, {len(certs_data) - created} already existed")


def seed_opportunities(db) -> None:
    opportunities_data = _load("opportunities.json")
    existing_titles = {(row.title, row.organization) for row in db.query(Opportunity).all()}
    created = 0
    for entry in opportunities_data:
        if (entry["title"], entry["organization"]) in existing_titles:
            continue
        payload = dict(entry)
        if payload.get("deadline"):
            payload["deadline"] = datetime.fromisoformat(payload["deadline"].replace("Z", "+00:00"))
        create_opportunity(db, OpportunityCreate(**payload))
        created += 1
    print(f"Opportunities: {created} created, {len(opportunities_data) - created} already existed")


def seed_all() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        skills_by_name = seed_skills(db)
        seed_careers(db, skills_by_name)
        seed_courses(db)
        seed_certifications(db)
        seed_opportunities(db)
        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
