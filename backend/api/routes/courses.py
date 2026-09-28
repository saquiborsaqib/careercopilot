from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import require_admin
from backend.database.connection import get_db
from backend.database.models.user import User
from backend.schemas.certification import CertificationCreate, CertificationResponse
from backend.schemas.course import CourseCreate, CourseResponse
from backend.services.certification_service import create_certification, get_certification, list_certifications
from backend.services.course_service import create_course, get_course, list_courses

router = APIRouter(tags=["courses"])


@router.get("/courses", response_model=list[CourseResponse])
def list_courses_route(level: str | None = None, db: Session = Depends(get_db)):
    return list_courses(db, level)


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course_route(data: CourseCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return create_course(db, data)


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_route(course_id: int, db: Session = Depends(get_db)):
    course = get_course(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/certifications", response_model=list[CertificationResponse])
def list_certifications_route(level: str | None = None, db: Session = Depends(get_db)):
    return list_certifications(db, level)


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def create_certification_route(data: CertificationCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    try:
        return create_certification(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/certifications/{certification_id}", response_model=CertificationResponse)
def get_certification_route(certification_id: int, db: Session = Depends(get_db)):
    certification = get_certification(db, certification_id)
    if certification is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification
