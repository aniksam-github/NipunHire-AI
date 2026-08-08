"""
Coding Repository — database operations for CodingChallenge and CodingSubmission documents using Beanie.
"""

from typing import Optional
from beanie import PydanticObjectId

from app.models.coding import CodingChallenge, CodingSubmission


async def create_challenge(challenge: CodingChallenge) -> CodingChallenge:
    """Inserts a new CodingChallenge document into MongoDB."""
    return await challenge.insert()


async def get_challenge_by_id(challenge_id: str) -> Optional[CodingChallenge]:
    """Fetches a CodingChallenge by ObjectId string."""
    try:
        obj_id = PydanticObjectId(challenge_id)
        return await CodingChallenge.get(obj_id)
    except Exception:
        return None


async def get_challenge_by_id_and_candidate(challenge_id: str, candidate_id: str) -> Optional[CodingChallenge]:
    """Fetches a CodingChallenge verifying candidate ownership."""
    try:
        c_oid = PydanticObjectId(challenge_id)
        cand_oid = PydanticObjectId(candidate_id)
        return await CodingChallenge.find_one(
            CodingChallenge.id == c_oid,
            CodingChallenge.candidate_id == cand_oid,
        )
    except Exception:
        return None


async def list_challenges_by_candidate(candidate_id: str, limit: int = 20) -> list[CodingChallenge]:
    """Queries coding challenges generated for a candidate."""
    try:
        cand_oid = PydanticObjectId(candidate_id)
        return (
            await CodingChallenge.find(CodingChallenge.candidate_id == cand_oid)
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )
    except Exception:
        return []


async def create_submission(submission: CodingSubmission) -> CodingSubmission:
    """Inserts a new CodingSubmission document into MongoDB."""
    return await submission.insert()


async def get_submission_by_id(submission_id: str) -> Optional[CodingSubmission]:
    """Fetches a CodingSubmission by ObjectId string."""
    try:
        obj_id = PydanticObjectId(submission_id)
        return await CodingSubmission.get(obj_id)
    except Exception:
        return None


async def get_submission_by_id_and_candidate(submission_id: str, candidate_id: str) -> Optional[CodingSubmission]:
    """Fetches a CodingSubmission verifying candidate ownership."""
    try:
        sub_oid = PydanticObjectId(submission_id)
        cand_oid = PydanticObjectId(candidate_id)
        return await CodingSubmission.find_one(
            CodingSubmission.id == sub_oid,
            CodingSubmission.candidate_id == cand_oid,
        )
    except Exception:
        return None


async def save_submission(submission: CodingSubmission) -> CodingSubmission:
    """Saves updates to an existing CodingSubmission instance."""
    await submission.save()
    return submission


async def list_submissions_by_candidate(candidate_id: str, limit: int = 20) -> list[CodingSubmission]:
    """Queries coding submissions for a candidate sorted by date."""
    try:
        cand_oid = PydanticObjectId(candidate_id)
        return (
            await CodingSubmission.find(CodingSubmission.candidate_id == cand_oid)
            .sort("-submitted_at")
            .limit(limit)
            .to_list()
        )
    except Exception:
        return []
