from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.ai.interview_ai import evaluate_answer, format_feedback_text, generate_question
from backend.database.models.career import Career
from backend.database.models.interview import InterviewAnswer, InterviewSession
from backend.schemas.interview import InterviewSessionCreate


def create_session(db: Session, data: InterviewSessionCreate) -> InterviewSession:
    session = InterviewSession(
        student_id=data.student_id,
        career_id=data.career_id,
        session_type=data.session_type,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int) -> InterviewSession | None:
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(selectinload(InterviewSession.answers))
    )
    return db.scalar(stmt)


def list_sessions(db: Session, student_id: int) -> list[InterviewSession]:
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.student_id == student_id)
        .order_by(InterviewSession.started_at.desc())
    )
    return list(db.scalars(stmt))


def _career_title(db: Session, career_id: int | None) -> str:
    if career_id is None:
        return "General"
    career = db.get(Career, career_id)
    return career.title if career else "General"


def ask_next_question(db: Session, session: InterviewSession) -> InterviewAnswer:
    career_title = _career_title(db, session.career_id)
    asked_so_far = [answer.question for answer in session.answers]
    question_text = generate_question(career_title, session.session_type.value, asked_so_far)

    answer_row = InterviewAnswer(session_id=session.id, question=question_text)
    db.add(answer_row)
    db.commit()
    db.refresh(answer_row)
    return answer_row


def submit_answer(db: Session, answer_row: InterviewAnswer, answer_text: str, career_title: str) -> InterviewAnswer:
    evaluation = evaluate_answer(answer_row.question, answer_text, career_title)
    answer_row.answer = answer_text
    answer_row.score = evaluation["score"]
    answer_row.feedback = format_feedback_text(evaluation)
    db.commit()
    db.refresh(answer_row)
    return answer_row


def get_answer(db: Session, answer_id: int) -> InterviewAnswer | None:
    return db.get(InterviewAnswer, answer_id)


def complete_session(db: Session, session: InterviewSession) -> InterviewSession:
    scored_answers = [a for a in session.answers if a.score is not None]
    overall_score = round(sum(a.score for a in scored_answers) / len(scored_answers), 1) if scored_answers else None

    strengths_count = sum(1 for a in scored_answers if a.score is not None and a.score >= 70)
    feedback_lines = [f"Completed {len(session.answers)} question(s)."]
    if overall_score is not None:
        feedback_lines.append(f"Overall score: {overall_score}/100.")
        feedback_lines.append(f"{strengths_count} of {len(scored_answers)} answers scored 70+.")

    session.overall_score = overall_score
    session.feedback = " ".join(feedback_lines)
    session.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session
