from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from routers import (
    student_profile,
    skill_assessment,
    skill_gap,
    roadmap,
    interview_coach,
    digital_twin,
    auth
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Velionx API...")
    # Initialize services on startup
    yield
    # Cleanup on shutdown
    logger.info("Shutting down Velionx API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Student Placement Preparation Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(student_profile.router, prefix="/api/profile", tags=["Student Profile Agent"])
app.include_router(skill_assessment.router, prefix="/api/assessment", tags=["Skill Assessment Agent"])
app.include_router(skill_gap.router, prefix="/api/skill-gap", tags=["Skill Gap Analyzer Agent"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["Roadmap Generator Agent"])
app.include_router(interview_coach.router, prefix="/api/interview", tags=["Interview Coach Agent"])
app.include_router(digital_twin.router, prefix="/api/digital-twin", tags=["Digital Twin"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Velionx API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "velionx-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
