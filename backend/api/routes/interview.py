from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.dependencies import ensure_student_owner, get_own_student_profile
from backend.core.security import get_current_user
from backend.database.connection import get_db
from backend.database.models.career import Career
from backend.database.models.student import StudentProfile
from backend.database.models.user import User
from backend.schemas.interview import InterviewAnswerResponse, InterviewSessionCreate, InterviewSessionResponse
from backend.services.interview_service import (
    ask_next_question,
    complete_session,
    create_session,
    get_answer,
    get_session,
    list_sessions,
    submit_answer,
)

router = APIRouter(prefix="/interview", tags=["interview"])


class AnswerSubmitRequest(BaseModel):
    answer: str


@router.get("/sessions/me", response_model=list[InterviewSessionResponse])
def list_my_sessions(profile: StudentProfile = Depends(get_own_student_profile), db: Session = Depends(get_db)):
    return list_sessions(db, profile.id)


@router.post("/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    data: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_owner(data.student_id, current_user, db)
    return create_session(db, data)


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
def get_one_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    ensure_student_owner(session.student_id, current_user, db)
    return session


@router.post("/sessions/{session_id}/next-question", response_model=InterviewAnswerResponse)
def next_question(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    ensure_student_owner(session.student_id, current_user, db)
    if session.completed_at is not None:
        raise HTTPException(status_code=400, detail="This interview session is already completed")
    return ask_next_question(db, session)


@router.post("/answers/{answer_id}/submit", response_model=InterviewAnswerResponse)
def submit(
    answer_id: int,
    data: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer_row = get_answer(db, answer_id)
    if answer_row is None:
        raise HTTPException(status_code=404, detail="Interview answer not found")
    session = get_session(db, answer_row.session_id)
    ensure_student_owner(session.student_id, current_user, db)

    career_title = "General"
    if session.career_id:
        career = db.get(Career, session.career_id)
        career_title = career.title if career else "General"

    return submit_answer(db, answer_row, data.answer, career_title)


@router.post("/sessions/{session_id}/complete", response_model=InterviewSessionResponse)
def complete(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found")
    ensure_student_owner(session.student_id, current_user, db)
    return complete_session(db, session)
