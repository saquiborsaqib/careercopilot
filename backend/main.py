from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.academic import router as academic_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.career import router as career_router
from backend.api.routes.courses import router as courses_router
from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.health import router as health_router
from backend.api.routes.interview import router as interview_router
from backend.api.routes.opportunities import router as opportunities_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.resume import router as resume_router
from backend.api.routes.roadmap import router as roadmap_router
from backend.api.routes.skills import router as skills_router
from backend.api.routes.students import router as students_router
from backend.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered career readiness and employability platform API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(academic_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(career_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(roadmap_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(opportunities_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/", tags=["root"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }
