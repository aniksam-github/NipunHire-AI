import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Holds the Motor client instance for the app's lifetime.
    """
    client: AsyncIOMotorClient | None = None


mongodb = MongoDB()


def _get_document_models() -> list:
    """
    Returns all Beanie Document models to register.
    """
    from app.models.user import User
    from app.models.job import Job
    from app.models.resume import Resume
    from app.models.resume_profile import ResumeProfile
    from app.models.resume_screening import ResumeScreening
    from app.models.profile import Profile
    from app.models.matching import JobMatch
    from app.models.application import Application
    from app.models.interview import InterviewSession
    from app.models.goal import CareerGoal
    from app.models.coding import CodingChallenge, CodingSubmission
    from app.models.coach import CoachMessage
    from app.models.notification import Notification
    from app.models.candidate_intelligence import ATSOptimizationSuggestion, ResumeOptimizationSuggestion
    from app.models.research import InterviewCheatRiskReport, ResumeAnomalyReport
    from app.models.audit_log import AuditLog
    from app.models.agent_session import AgentSession

    return [
        User,
        Job,
        Resume,
        ResumeProfile,
        ResumeScreening,
        Profile,
        JobMatch,
        Application,
        InterviewSession,
        CareerGoal,
        CodingChallenge,
        CodingSubmission,
        CoachMessage,
        Notification,
        ResumeOptimizationSuggestion,
        ATSOptimizationSuggestion,
        ResumeAnomalyReport,
        InterviewCheatRiskReport,
        AuditLog,
        AgentSession,
    ]


async def connect_to_mongo():
    logger.info("Connecting to MongoDB at %s...", settings.MONGODB_URI)
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = mongodb.client[settings.DATABASE_NAME]

    models = _get_document_models()
    await init_beanie(database=database, document_models=models)
    logger.info("MongoDB connected and Beanie initialized with %d models.", len(models))


async def close_mongo_connection():
    if mongodb.client:
        logger.info("Closing MongoDB connection...")
        mongodb.client.close()
        logger.info("MongoDB connection closed.")
