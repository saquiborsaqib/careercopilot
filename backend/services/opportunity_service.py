from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.opportunity import Opportunity
from backend.database.models.enums import OpportunityType
from backend.schemas.opportunity import OpportunityCreate


def list_opportunities(
    db: Session,
    opportunity_type: OpportunityType | None = None,
    location: str | None = None,
) -> list[Opportunity]:
    stmt = select(Opportunity)
    if opportunity_type:
        stmt = stmt.where(Opportunity.opportunity_type == opportunity_type)
    if location:
        stmt = stmt.where(Opportunity.location == location)
    return list(db.scalars(stmt.order_by(Opportunity.created_at.desc())))


def get_opportunity(db: Session, opportunity_id: int) -> Opportunity | None:
    return db.get(Opportunity, opportunity_id)


def create_opportunity(db: Session, data: OpportunityCreate) -> Opportunity:
    opportunity = Opportunity(**data.model_dump())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def match_opportunities_for_student(
    db: Session,
    student,
    opportunity_type: OpportunityType | None = None,
    limit: int = 20,
) -> list[Opportunity]:
    """Deterministic eligibility-aware matching: filters by type/location relevance.

    Government/job eligibility text is matched against the student's degree and
    branch as a simple containment heuristic; this keeps eligibility decisions
    in Python rather than delegating them to an LLM.
    """
    candidates = list_opportunities(db, opportunity_type=opportunity_type)
    scored: list[tuple[float, Opportunity]] = []
    for opportunity in candidates:
        score = 0.0
        if student.preferred_location and opportunity.location:
            if student.preferred_location.strip().lower() == opportunity.location.strip().lower():
                score += 2.0
        if opportunity.eligibility:
            eligibility_text = opportunity.eligibility.lower()
            if student.degree and student.degree.lower() in eligibility_text:
                score += 1.5
            if student.branch and student.branch.lower() in eligibility_text:
                score += 1.5
            if "any" in eligibility_text or "all graduates" in eligibility_text:
                score += 1.0
        else:
            score += 0.5
        scored.append((score, opportunity))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [opportunity for _, opportunity in scored[:limit]]
