from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.ai.career_personalization import explain_career_match
from backend.database.models.career import Career
from backend.database.models.certification import Certification
from backend.database.models.course import Course
from backend.database.models.enums import RecommendationType
from backend.database.models.recommendation import Recommendation
from backend.database.models.student import StudentProfile
from backend.services.career_engine_service import compute_skill_gap, recommend_careers
from backend.vector.faiss_index import VectorIndex

SEMANTIC_MATCH_THRESHOLD = 0.2


def list_recommendations(
    db: Session, student_id: int, recommendation_type: RecommendationType | None = None
) -> list[Recommendation]:
    stmt = select(Recommendation).where(Recommendation.student_id == student_id)
    if recommendation_type:
        stmt = stmt.where(Recommendation.recommendation_type == recommendation_type)
    return list(db.scalars(stmt.order_by(Recommendation.score.desc().nullslast())))


def _student_summary(student: StudentProfile) -> str:
    parts = [p for p in [student.degree, student.branch, student.career_interest] if p]
    return ", ".join(parts) if parts else "a student building their career profile"


def generate_career_recommendations(db: Session, student: StudentProfile, top_n: int = 3) -> list[Recommendation]:
    matches = recommend_careers(db, student, top_n=top_n)
    student_summary = _student_summary(student)
    created: list[Recommendation] = []

    for match in matches:
        gap_report = compute_skill_gap(db, student.id, match.career.id)
        matched_names = [item.skill_name for item in gap_report.developed]
        gap_names = [item.skill_name for item in gap_report.gaps]

        explanation = explain_career_match(
            student_summary, match.career.title, match.overall_score, matched_names, gap_names
        )

        existing = db.scalar(
            select(Recommendation).where(
                Recommendation.student_id == student.id,
                Recommendation.recommendation_type == RecommendationType.CAREER,
                Recommendation.career_id == match.career.id,
            )
        )
        if existing:
            existing.score = match.overall_score
            existing.explanation = explanation
            recommendation = existing
        else:
            recommendation = Recommendation(
                student_id=student.id,
                recommendation_type=RecommendationType.CAREER,
                career_id=match.career.id,
                title=match.career.title,
                explanation=explanation,
                score=match.overall_score,
                source="career_engine",
            )
            db.add(recommendation)
        created.append(recommendation)

    db.commit()
    for rec in created:
        db.refresh(rec)
    return created


def generate_course_recommendations(db: Session, student: StudentProfile, career_id: int, top_n: int = 5) -> list[Recommendation]:
    career = db.get(Career, career_id)
    if career is None:
        raise ValueError("Career not found")

    gap_report = compute_skill_gap(db, student.id, career_id)
    if not gap_report.gaps:
        return []

    courses = list(db.scalars(select(Course)))
    course_index = VectorIndex("courses")
    course_index.build([c.id for c in courses], [f"{c.title}. {c.description or ''}" for c in courses])
    courses_by_id = {c.id: c for c in courses}

    existing_by_course_id = {
        rec.course_id: rec
        for rec in db.scalars(
            select(Recommendation).where(
                Recommendation.student_id == student.id,
                Recommendation.recommendation_type == RecommendationType.COURSE,
            )
        )
    }
    created: list[Recommendation] = []
    handled_course_ids: set[int] = set()

    for gap in gap_report.gaps[:5]:
        best_course, best_score = _best_catalog_match(
            gap.skill_name, courses, lambda c: f"{c.title}. {c.description or ''}", course_index, courses_by_id
        )
        if best_course is None or best_course.id in handled_course_ids:
            continue
        handled_course_ids.add(best_course.id)

        existing = existing_by_course_id.get(best_course.id)
        if existing:
            existing.score = best_score
            recommendation = existing
        else:
            recommendation = Recommendation(
                student_id=student.id,
                recommendation_type=RecommendationType.COURSE,
                course_id=best_course.id,
                title=best_course.title,
                explanation=f"Recommended to close your '{gap.skill_name}' skill gap for {career.title}.",
                score=best_score,
                source="skill_gap_matcher",
            )
            db.add(recommendation)
        created.append(recommendation)
        if len(created) >= top_n:
            break

    db.commit()
    for rec in created:
        db.refresh(rec)
    return created


def generate_certification_recommendations(db: Session, student: StudentProfile, career_id: int, top_n: int = 3) -> list[Recommendation]:
    career = db.get(Career, career_id)
    if career is None:
        raise ValueError("Career not found")

    gap_report = compute_skill_gap(db, student.id, career_id)
    if not gap_report.gaps:
        return []

    certifications = list(db.scalars(select(Certification)))
    cert_index = VectorIndex("certifications")
    cert_index.build([c.id for c in certifications], [f"{c.name}. {c.description or ''}" for c in certifications])
    certifications_by_id = {c.id: c for c in certifications}

    existing_by_cert_id = {
        rec.certification_id: rec
        for rec in db.scalars(
            select(Recommendation).where(
                Recommendation.student_id == student.id,
                Recommendation.recommendation_type == RecommendationType.CERTIFICATION,
            )
        )
    }
    created: list[Recommendation] = []
    handled_cert_ids: set[int] = set()

    for gap in gap_report.gaps[:5]:
        best_cert, best_score = _best_catalog_match(
            gap.skill_name, certifications, lambda c: f"{c.name}. {c.description or ''}", cert_index, certifications_by_id
        )
        if best_cert is None or best_cert.id in handled_cert_ids:
            continue
        handled_cert_ids.add(best_cert.id)

        existing = existing_by_cert_id.get(best_cert.id)
        if existing:
            existing.score = best_score
            recommendation = existing
        else:
            recommendation = Recommendation(
                student_id=student.id,
                recommendation_type=RecommendationType.CERTIFICATION,
                certification_id=best_cert.id,
                title=best_cert.name,
                explanation=f"Relevant certification for your '{gap.skill_name}' skill gap toward {career.title}.",
                score=best_score,
                source="skill_gap_matcher",
            )
            db.add(recommendation)
        created.append(recommendation)
        if len(created) >= top_n:
            break

    db.commit()
    for rec in created:
        db.refresh(rec)
    return created


def _best_catalog_match(
    skill_name: str,
    catalog_items: list,
    text_getter,
    index: VectorIndex,
    items_by_id: dict[int, object],
) -> tuple[object | None, float]:
    """Find the catalog item best matching a skill-gap name.

    Substring containment is checked first (a course literally named after
    the skill is an obvious match). Otherwise semantic similarity is looked
    up via a FAISS-backed vector index (`index`) built once for the whole
    catalog, rather than embedding every catalog item again per skill gap.
    """
    skill_lower = skill_name.lower()
    for item in catalog_items:
        if skill_lower in text_getter(item).lower():
            return item, 95.0

    for item_id, similarity in index.search(skill_name, top_k=1):
        score = round(max(0.0, min(1.0, similarity)) * 100, 1)
        if score < SEMANTIC_MATCH_THRESHOLD * 100:
            return None, 0.0
        return items_by_id.get(item_id), score

    return None, 0.0
