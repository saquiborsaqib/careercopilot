"""Deterministic career intelligence: skill-gap analysis and career scoring.

Per the project's hybrid-AI architecture, factual eligibility and scoring
live here in plain Python. Semantic similarity (backend.ai.embeddings) only
nudges the ranking; it never overrides a deterministic skill-coverage score,
and natural-language explanations are layered on top by backend.ai.career_personalization.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.ai.embeddings import semantic_similarity
from backend.database.models.career import Career
from backend.database.models.skill import CareerSkill, Skill, StudentSkill
from backend.database.models.student import StudentProfile
from backend.services.scoring_utils import IMPORTANCE_WEIGHT, meets_minimum
from backend.vector.faiss_index import get_index


@dataclass
class SkillGapItem:
    skill_id: int
    skill_name: str
    importance: str
    minimum_level: str
    student_level: str | None
    status: str  # "developed" | "gap"
    priority: str  # "high" | "medium" | "low"


@dataclass
class SkillGapReport:
    career_id: int
    career_title: str
    coverage_percent: float
    developed: list[SkillGapItem] = field(default_factory=list)
    gaps: list[SkillGapItem] = field(default_factory=list)


@dataclass
class CareerMatch:
    career: Career
    skill_match_score: float
    semantic_score: float
    overall_score: float
    matched_skill_count: int
    required_skill_count: int


def _priority_for_importance(importance) -> str:
    value = importance.value if hasattr(importance, "value") else str(importance)
    if value == "essential":
        return "high"
    if value == "important":
        return "high"
    if value == "useful":
        return "medium"
    return "low"


def _student_skill_map(db: Session, student_id: int) -> dict[int, StudentSkill]:
    rows = db.scalars(
        select(StudentSkill)
        .where(StudentSkill.student_id == student_id)
        .options(selectinload(StudentSkill.skill))
    )
    return {row.skill_id: row for row in rows}


def compute_skill_gap(db: Session, student_id: int, career_id: int) -> SkillGapReport:
    career = db.get(Career, career_id)
    if career is None:
        raise ValueError("Career not found")

    career_skills = db.scalars(
        select(CareerSkill)
        .where(CareerSkill.career_id == career_id)
        .options(selectinload(CareerSkill.skill))
    ).all()
    student_skills = _student_skill_map(db, student_id)

    report = SkillGapReport(career_id=career.id, career_title=career.title, coverage_percent=0.0)
    if not career_skills:
        return report

    developed_weight = 0.0
    total_weight = 0.0
    for cs in career_skills:
        weight = IMPORTANCE_WEIGHT[cs.importance]
        total_weight += weight
        student_skill = student_skills.get(cs.skill_id)
        has_skill = student_skill is not None and meets_minimum(student_skill.proficiency_level, cs.minimum_level)
        item = SkillGapItem(
            skill_id=cs.skill_id,
            skill_name=cs.skill.name,
            importance=cs.importance.value,
            minimum_level=cs.minimum_level.value,
            student_level=student_skill.proficiency_level.value if student_skill else None,
            status="developed" if has_skill else "gap",
            priority="low" if has_skill else _priority_for_importance(cs.importance),
        )
        if has_skill:
            developed_weight += weight
            report.developed.append(item)
        else:
            report.gaps.append(item)

    report.gaps.sort(key=lambda i: {"high": 0, "medium": 1, "low": 2}[i.priority])
    report.coverage_percent = round((developed_weight / total_weight) * 100, 1) if total_weight else 0.0
    return report


def _career_profile_text(career: Career) -> str:
    parts = [career.title]
    if career.description:
        parts.append(career.description)
    if career.industry:
        parts.append(career.industry)
    return ". ".join(parts)


def _student_profile_text(student: StudentProfile, student_skills: dict[int, StudentSkill]) -> str:
    parts = []
    if student.degree:
        parts.append(student.degree)
    if student.branch:
        parts.append(student.branch)
    if student.career_interest:
        parts.append(student.career_interest)
    skill_names = [row.skill.name for row in student_skills.values() if row.skill is not None]
    if skill_names:
        parts.append(", ".join(skill_names))
    return ". ".join(parts) if parts else ""


def score_career_for_student(db: Session, student: StudentProfile, career: Career) -> CareerMatch:
    student_skills = _student_skill_map(db, student.id)
    matched, developed_weight, total_weight, career_skills = _skill_match_for_career(db, student.id, career.id, student_skills)
    skill_match_score = (developed_weight / total_weight) * 100 if total_weight else 0.0

    student_text = _student_profile_text(student, student_skills)
    career_text = _career_profile_text(career)
    semantic_score = semantic_similarity(student_text, career_text) * 100 if student_text else 0.0

    overall_score = round((0.7 * skill_match_score) + (0.3 * semantic_score), 1)
    return CareerMatch(
        career=career,
        skill_match_score=round(skill_match_score, 1),
        semantic_score=round(semantic_score, 1),
        overall_score=overall_score,
        matched_skill_count=matched,
        required_skill_count=len(career_skills),
    )


def _skill_match_for_career(
    db: Session, student_id: int, career_id: int, student_skills: dict[int, StudentSkill]
) -> tuple[int, float, float, list]:
    career_skills = db.scalars(
        select(CareerSkill).where(CareerSkill.career_id == career_id).options(selectinload(CareerSkill.skill))
    ).all()

    matched = 0
    developed_weight = 0.0
    total_weight = 0.0
    for cs in career_skills:
        weight = IMPORTANCE_WEIGHT[cs.importance]
        total_weight += weight
        student_skill = student_skills.get(cs.skill_id)
        if student_skill is not None and meets_minimum(student_skill.proficiency_level, cs.minimum_level):
            matched += 1
            developed_weight += weight

    return matched, developed_weight, total_weight, career_skills


def recommend_careers(db: Session, student: StudentProfile, top_n: int = 5) -> list[CareerMatch]:
    """Rank every career for this student.

    Skill coverage is always computed deterministically in Python. Semantic
    fit is retrieved via a FAISS-backed vector index (falls back to a NumPy
    cosine scan without the faiss package) built over all career profile
    texts and queried once with the student's profile text, rather than
    doing an O(n) pairwise embedding comparison per career.
    """
    careers = db.scalars(select(Career)).all()
    if not careers:
        return []

    student_skills = _student_skill_map(db, student.id)
    student_text = _student_profile_text(student, student_skills)

    semantic_scores: dict[int, float] = {}
    if student_text:
        index = get_index("careers")
        index.build([c.id for c in careers], [_career_profile_text(c) for c in careers])
        semantic_scores = dict(index.search(student_text, top_k=len(careers)))

    matches: list[CareerMatch] = []
    for career in careers:
        matched, developed_weight, total_weight, career_skills = _skill_match_for_career(
            db, student.id, career.id, student_skills
        )
        skill_match_score = (developed_weight / total_weight) * 100 if total_weight else 0.0
        semantic_score = max(0.0, min(1.0, semantic_scores.get(career.id, 0.0))) * 100

        overall_score = round((0.7 * skill_match_score) + (0.3 * semantic_score), 1)
        matches.append(
            CareerMatch(
                career=career,
                skill_match_score=round(skill_match_score, 1),
                semantic_score=round(semantic_score, 1),
                overall_score=overall_score,
                matched_skill_count=matched,
                required_skill_count=len(career_skills),
            )
        )

    matches.sort(key=lambda m: m.overall_score, reverse=True)
    return matches[:top_n]
