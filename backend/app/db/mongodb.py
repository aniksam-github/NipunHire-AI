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
    ]


async def connect_to_mongo() -> None:
    """
    Initializes the Motor client and Beanie ODM.
    """
    logger.info("Connecting to MongoDB at %s", settings.DATABASE_NAME)

    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)

    # Fail fast: ping forces a round-trip instead of lazy-connecting silently
    await mongodb.client.admin.command("ping")

    await init_beanie(
        database=mongodb.client[settings.DATABASE_NAME],
        document_models=_get_document_models(),
    )

    logger.info("MongoDB connected and Beanie initialized successfully")


async def close_mongo_connection() -> None:
    """
    Closes the Motor client.
    """
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    if mongodb.client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo() first.")
    return mongodb.client[settings.DATABASE_NAME]
