from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.ai.career_personalization import summarize_roadmap
from backend.core.dependencies import ensure_student_owner, get_own_student_profile
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.enums import RoadmapItemStatus
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.roadmap import RoadmapItemResponse, RoadmapResponse
from backend.services.roadmap_service import (
    generate_roadmap,
    get_roadmap,
    get_roadmap_item,
    list_roadmaps,
    update_roadmap_item_status,
)

router = APIRouter(prefix="/roadmaps", tags=["roadmap"])


@router.get("/me", response_model=list[RoadmapResponse])
def list_my_roadmaps(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return list_roadmaps(db, profile.id)


@router.post("/generate/{career_id}", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
def generate(career_id: int, profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    try:
        return generate_roadmap(db, profile.id, career_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_one(roadmap_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roadmap = get_roadmap(db, roadmap_id)
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    ensure_student_owner(roadmap.student_id, current_user, db)
    return roadmap


@router.get("/{roadmap_id}/narrative")
def get_narrative(roadmap_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roadmap = get_roadmap(db, roadmap_id)
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    ensure_student_owner(roadmap.student_id, current_user, db)
    item_titles = [item.title for item in sorted(roadmap.items, key=lambda i: i.sequence)]
    narrative = summarize_roadmap(roadmap.career.title if roadmap.career else roadmap.title, item_titles)
    return {"narrative": narrative}


@router.patch("/items/{item_id}", response_model=RoadmapItemResponse)
def update_item_status(
    item_id: int,
    status_value: RoadmapItemStatus = Body(embed=True, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = get_roadmap_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    roadmap = get_roadmap(db, item.roadmap_id)
    ensure_student_owner(roadmap.student_id, current_user, db)
    return update_roadmap_item_status(db, item, status_value)
