from sqlalchemy.orm import Session

from backend.database.models.enums import RecommendationType
from backend.database.models.resume import Resume
from backend.database.models.student import StudentProfile
from backend.services.career_engine_service import compute_skill_gap, recommend_careers
from backend.services.recommendation_service import list_recommendations
from backend.services.resume_service import list_resumes
from backend.services.roadmap_service import list_roadmaps

PROFILE_FIELDS = ["college", "degree", "branch", "graduation_year", "cgpa", "career_interest"]


def _profile_completeness(student: StudentProfile) -> float:
    filled = sum(1 for field in PROFILE_FIELDS if getattr(student, field) not in (None, ""))
    return round((filled / len(PROFILE_FIELDS)) * 100, 1)


def _roadmap_progress(db: Session, student_id: int) -> tuple[float, dict | None]:
    roadmaps = list_roadmaps(db, student_id)
    if not roadmaps:
        return 0.0, None
    roadmap = roadmaps[0]
    if not roadmap.items:
        return 0.0, {"id": roadmap.id, "title": roadmap.title, "status": roadmap.status.value, "items": []}

    completed = sum(1 for item in roadmap.items if item.status.value == "completed")
    progress = round((completed / len(roadmap.items)) * 100, 1)
    items = sorted(roadmap.items, key=lambda i: i.sequence)
    return progress, {
        "id": roadmap.id,
        "title": roadmap.title,
        "status": roadmap.status.value,
        "progress_percent": progress,
        "items": [{"id": i.id, "title": i.title, "sequence": i.sequence, "status": i.status.value} for i in items],
    }


def build_dashboard(db: Session, student: StudentProfile) -> dict:
    profile_completeness = _profile_completeness(student)

    top_matches = recommend_careers(db, student, top_n=1)
    top_career = None
    skill_gaps: list[dict] = []
    if top_matches:
        match = top_matches[0]
        gap_report = compute_skill_gap(db, student.id, match.career.id)
        top_career = {
            "id": match.career.id,
            "title": match.career.title,
            "overall_score": match.overall_score,
        }
        skill_gaps = [
            {"skill_name": g.skill_name, "priority": g.priority, "importance": g.importance}
            for g in gap_report.gaps[:5]
        ]

    resumes: list[Resume] = list_resumes(db, student.id)
    resume_uploaded = len(resumes) > 0

    roadmap_progress_percent, roadmap_summary = _roadmap_progress(db, student.id)

    course_recommendations = list_recommendations(db, student.id, RecommendationType.COURSE)[:5]

    weights_sum = 0.0
    score_sum = 0.0
    score_sum += 0.35 * profile_completeness
    weights_sum += 0.35
    if top_career is not None:
        score_sum += 0.40 * top_career["overall_score"]
        weights_sum += 0.40
    score_sum += 0.10 * (100 if resume_uploaded else 0)
    weights_sum += 0.10
    if roadmap_summary is not None:
        score_sum += 0.15 * roadmap_progress_percent
        weights_sum += 0.15

    readiness_score = round(score_sum / weights_sum, 1) if weights_sum else 0.0

    return {
        "career_readiness_score": readiness_score,
        "profile_completeness_percent": profile_completeness,
        "recommended_career": top_career,
        "skill_gaps": skill_gaps,
        "resume_uploaded": resume_uploaded,
        "roadmap": roadmap_summary,
        "recommended_courses": [
            {"id": rec.id, "title": rec.title, "explanation": rec.explanation, "score": rec.score}
            for rec in course_recommendations
        ],
    }
