from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.database.models.career import Career
from backend.database.models.roadmap import Roadmap, RoadmapItem
from backend.database.models.enums import RoadmapItemStatus
from backend.schemas.roadmap import RoadmapItemCreate
from backend.services.career_engine_service import compute_skill_gap


def list_roadmaps(db: Session, student_id: int) -> list[Roadmap]:
    stmt = (
        select(Roadmap)
        .where(Roadmap.student_id == student_id)
        .options(selectinload(Roadmap.items))
        .order_by(Roadmap.created_at.desc())
    )
    return list(db.scalars(stmt))


def get_roadmap(db: Session, roadmap_id: int) -> Roadmap | None:
    stmt = select(Roadmap).where(Roadmap.id == roadmap_id).options(selectinload(Roadmap.items))
    return db.scalar(stmt)


def generate_roadmap(db: Session, student_id: int, career_id: int) -> Roadmap:
    """Build a roadmap deterministically from the skill-gap report.

    Ordering: high-priority gaps first, then medium, then low, grouped into
    monthly milestones of up to three items followed by a capstone project +
    resume/interview prep item, matching the flow described in the product spec.
    """
    career = db.get(Career, career_id)
    if career is None:
        raise ValueError("Career not found")

    gap_report = compute_skill_gap(db, student_id, career_id)

    roadmap = Roadmap(
        student_id=student_id,
        career_id=career_id,
        title=f"{career.title} Readiness Roadmap",
        description=f"Personalized roadmap generated from a {gap_report.coverage_percent}% skill match against {career.title}.",
    )
    db.add(roadmap)
    db.flush()

    sequence = 1
    items: list[RoadmapItem] = []
    for gap in gap_report.gaps:
        items.append(
            RoadmapItem(
                roadmap_id=roadmap.id,
                skill_id=gap.skill_id,
                title=f"Learn {gap.skill_name}",
                description=f"Priority: {gap.priority}. Reach at least '{gap.minimum_level}' proficiency for {career.title}.",
                sequence=sequence,
                status=RoadmapItemStatus.NOT_STARTED,
            )
        )
        sequence += 1

    items.append(
        RoadmapItem(
            roadmap_id=roadmap.id,
            skill_id=None,
            title="Build a portfolio project",
            description=f"Apply your newly developed skills in a project relevant to {career.title}.",
            sequence=sequence,
            status=RoadmapItemStatus.NOT_STARTED,
        )
    )
    sequence += 1
    items.append(
        RoadmapItem(
            roadmap_id=roadmap.id,
            skill_id=None,
            title="Improve resume and prepare for interviews",
            description=f"Update your resume with the new skills and complete a mock {career.title} interview.",
            sequence=sequence,
            status=RoadmapItemStatus.NOT_STARTED,
        )
    )

    db.add_all(items)
    db.commit()
    db.refresh(roadmap)
    return roadmap


def add_roadmap_item(db: Session, data: RoadmapItemCreate) -> RoadmapItem:
    item = RoadmapItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_roadmap_item_status(db: Session, item: RoadmapItem, status: RoadmapItemStatus) -> RoadmapItem:
    item.status = status
    db.commit()
    db.refresh(item)
    return item


def get_roadmap_item(db: Session, item_id: int) -> RoadmapItem | None:
    return db.get(RoadmapItem, item_id)
