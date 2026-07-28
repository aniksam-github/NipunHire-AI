import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Holds the Motor client instance for the app's lifetime.

    Kept as a class (not bare module globals) so it's explicit state
    that lives on one object, easy to reason about and to reset in tests.
    """
    client: AsyncIOMotorClient | None = None


mongodb = MongoDB()


def _get_document_models() -> list:
    """
    Returns all Beanie Document models to register.

    Kept as a function (not a module-level import list) to avoid
    circular imports as models/ grows — models are imported lazily,
    only when the DB actually initializes.
    """
    from app.models.user import User
    from app.models.job import Job
    from app.models.resume import Resume
    from app.models.profile import Profile
    from app.models.matching import JobMatch
    from app.models.application import Application
    from app.models.interview import InterviewSession
    from app.models.goal import CareerGoal
    from app.models.coding import CodingSubmission
    from app.models.coach import CoachMessage
    from app.models.notification import Notification

    return [
        User,
        Job,
        Resume,
        Profile,
        JobMatch,
        Application,
        InterviewSession,
        CareerGoal,
        CodingSubmission,
        CoachMessage,
        Notification,
    ]


async def connect_to_mongo() -> None:
    """
    Initializes the Motor client and Beanie ODM.

    Called once from main.py's lifespan startup. Raises immediately
    if the connection fails — we want the app to refuse to start
    rather than serve requests against a dead DB.
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
    Closes the Motor client. Called from main.py's lifespan shutdown.
    """
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """
    Accessor for the raw database handle, for cases needing direct
    PyMongo/Motor operations outside Beanie (e.g. aggregation pipelines,
    vector search later). Repositories should prefer Beanie models;
    this is an escape hatch, not the default path.
    """
    if mongodb.client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo() first.")
    return mongodb.client[settings.DATABASE_NAME]
