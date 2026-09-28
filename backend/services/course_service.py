from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.course import Course
from backend.schemas.course import CourseCreate


def list_courses(db: Session, level: str | None = None) -> list[Course]:
    stmt = select(Course)
    if level:
        stmt = stmt.where(Course.level == level)
    return list(db.scalars(stmt.order_by(Course.title)))


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def create_course(db: Session, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
