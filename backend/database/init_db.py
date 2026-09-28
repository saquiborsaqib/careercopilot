from sqlalchemy import inspect
from .base import Base
from .connection import engine
EXPECTED={"users","student_profiles","academic_records","skills","student_skills","careers","career_skills","courses","certifications","resumes","opportunities","roadmaps","roadmap_items","interview_sessions","interview_answers","recommendations"}
def init_db():
 Base.metadata.create_all(bind=engine)
 actual=set(inspect(engine).get_table_names()); missing=EXPECTED-actual
 if missing: raise RuntimeError(f"Missing tables: {sorted(missing)}")
 print(f"AI CareerPilot SQLite initialized: {len(actual)} tables")
 for t in sorted(EXPECTED): print(f" - {t}")
if __name__=='__main__': init_db()
