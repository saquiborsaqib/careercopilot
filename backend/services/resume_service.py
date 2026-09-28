from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.ai.resume_ai import improve_resume
from backend.core.config import settings
from backend.database.models.enums import AnalysisStatus, ProficiencyLevel, ResumeFileType, SkillSource
from backend.database.models.resume import Resume
from backend.database.models.skill import Skill, StudentSkill
from backend.processing.docx_parser import extract_text_from_docx
from backend.processing.pdf_parser import extract_text_from_pdf
from backend.processing.skill_extractor import extract_skills_from_text

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ResumeFileType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ResumeFileType.DOCX,
}
ALLOWED_EXTENSIONS = {".pdf": ResumeFileType.PDF, ".docx": ResumeFileType.DOCX}


def resolve_file_type(upload: UploadFile) -> ResumeFileType:
    extension = Path(upload.filename or "").suffix.lower()
    if extension in ALLOWED_EXTENSIONS:
        return ALLOWED_EXTENSIONS[extension]
    if upload.content_type in ALLOWED_CONTENT_TYPES:
        return ALLOWED_CONTENT_TYPES[upload.content_type]
    raise ValueError("Only PDF and DOCX resumes are supported")


def save_upload(upload: UploadFile, student_id: int, file_type: ResumeFileType) -> tuple[str, str]:
    uploads_root = Path(settings.uploads_dir) / "resumes" / str(student_id)
    uploads_root.mkdir(parents=True, exist_ok=True)

    extension = ".pdf" if file_type == ResumeFileType.PDF else ".docx"
    stored_name = f"{uuid4().hex}{extension}"
    destination = uploads_root / stored_name

    with destination.open("wb") as buffer:
        buffer.write(upload.file.read())

    return str(destination), upload.filename or stored_name


def create_resume(db: Session, student_id: int, file_name: str, file_path: str, file_type: ResumeFileType) -> Resume:
    resume = Resume(
        student_id=student_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        analysis_status=AnalysisStatus.PENDING,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session, student_id: int) -> list[Resume]:
    return list(db.scalars(select(Resume).where(Resume.student_id == student_id).order_by(Resume.uploaded_at.desc())))


def get_resume(db: Session, resume_id: int) -> Resume | None:
    return db.get(Resume, resume_id)


def process_resume(db: Session, resume: Resume) -> Resume:
    """Extract text synchronously. Errors leave the resume in FAILED status
    rather than raising, so an upload never 500s on a malformed file."""
    resume.analysis_status = AnalysisStatus.PROCESSING
    db.commit()

    try:
        if resume.file_type == ResumeFileType.PDF:
            text = extract_text_from_pdf(resume.file_path)
        else:
            text = extract_text_from_docx(resume.file_path)
        resume.extracted_text = text
        resume.analysis_status = AnalysisStatus.COMPLETED
    except Exception:
        resume.analysis_status = AnalysisStatus.FAILED
    db.commit()
    db.refresh(resume)
    return resume


def sync_skills_from_resume(db: Session, resume: Resume) -> list[Skill]:
    if not resume.extracted_text:
        return []

    catalog_names = [row[0] for row in db.execute(select(Skill.name)).all()]
    matched_names = extract_skills_from_text(resume.extracted_text, catalog_names)
    if not matched_names:
        return []

    skills = list(db.scalars(select(Skill).where(Skill.name.in_(matched_names))))
    existing = {
        row.skill_id
        for row in db.scalars(select(StudentSkill).where(StudentSkill.student_id == resume.student_id))
    }

    for skill in skills:
        if skill.id in existing:
            continue
        db.add(
            StudentSkill(
                student_id=resume.student_id,
                skill_id=skill.id,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source=SkillSource.AI_EXTRACTED,
            )
        )
    db.commit()
    return skills


def generate_resume_improvement(resume: Resume, target_career: str | None = None) -> str:
    if not resume.extracted_text:
        return "No extracted text available yet. Please wait for resume processing to complete."
    return improve_resume(resume.extracted_text, target_career)
