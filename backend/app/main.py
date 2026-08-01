import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.resumes import router as resumes_router
from app.api.profile import router as profile_router
from app.api.matching import router as matching_router
from app.api.applications import router as applications_router
from app.api.dashboard import router as dashboard_router
from app.api.interviews import router as interviews_router
from app.api.goals import router as goals_router
from app.api.coding import router as coding_router
from app.api.coach import router as coach_router
from app.api.settings import router as settings_router
from app.api.notifications import router as notifications_router
from app.api.candidate_intelligence import router as candidate_intelligence_router
from app.api.recruiter import router as recruiter_router
from app.api.research import router as research_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.db.mongodb import connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="NipunHire AI — Autonomous End-to-End AI Hiring & Candidate Evaluation Platform",
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- API Routers ----
app.include_router(auth_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(matching_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(interviews_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(coding_router, prefix="/api/v1")
app.include_router(coach_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(candidate_intelligence_router, prefix="/api/v1")
app.include_router(recruiter_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"project": settings.PROJECT_NAME, "version": settings.VERSION, "status": "running"}
