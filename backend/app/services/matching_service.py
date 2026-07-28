"""
Matching Service — Job Description vs Resume semantic skill gap & match score engine.
"""

import logging
from beanie import PydanticObjectId

from app.core.exceptions import EntityNotFoundError
from app.models.matching import JobMatch
from app.repositories import job_repo, resume_repo, matching_repo
from app.schemas.matching import MatchResponse

logger = logging.getLogger(__name__)


def _build_match_response(m: JobMatch) -> MatchResponse:
    """Maps a JobMatch document to MatchResponse."""
    return MatchResponse(
        id=str(m.id),
        candidate_id=str(m.candidate_id),
        job_id=str(m.job_id),
        resume_id=str(m.resume_id) if m.resume_id else None,
        match_score=m.match_score,
        matched_skills=m.matched_skills,
        missing_required_skills=m.missing_required_skills,
        missing_optional_skills=m.missing_optional_skills,
        strengths=m.strengths,
        weaknesses=m.weaknesses,
        application_readiness_score=m.application_readiness_score,
        recommendations=m.recommendations,
    )


async def evaluate_job_match(
    candidate_id: str,
    job_id: str,
    resume_id: str | None = None,
) -> MatchResponse:
    """
    Compares candidate's primary or specified resume against job requirements,
    extracts matched & missing skills, calculates match score (0-100%), and returns readiness report.
    """
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise EntityNotFoundError(entity="Job", identifier=job_id)

    # Resolve resume
    resume = None
    if resume_id:
        resume = await resume_repo.get_by_id(resume_id)
    else:
        resumes = await resume_repo.list_by_candidate(candidate_id)
        if resumes:
            resume = resumes[0]

    candidate_skills = [s.lower() for s in (resume.extracted_skills if resume else [])]

    # Required & Optional skills comparison
    job_required = job.required_skills
    job_optional = job.optional_skills

    matched_skills: list[str] = []
    missing_required: list[str] = []
    missing_optional: list[str] = []

    for req in job_required:
        if req.lower() in candidate_skills:
            matched_skills.append(req)
        else:
            missing_required.append(req)

    for opt in job_optional:
        if opt.lower() in candidate_skills:
            matched_skills.append(opt)
        else:
            missing_optional.append(opt)

    # Calculate Match Score
    total_req = max(1, len(job_required))
    req_match_ratio = len(matched_skills) / total_req
    match_score = round(min(99.0, req_match_ratio * 100.0), 1)

    # Strengths & Weaknesses
    strengths = [f"Strong alignment in {skill}" for skill in matched_skills[:3]]
    if not strengths:
        strengths.append("Broad foundation in technical concepts.")

    weaknesses = [f"Missing key requirement: {skill}" for skill in missing_required[:3]]

    # Readiness Score
    readiness_score = int(match_score * 0.9)
    if len(missing_required) == 0:
        readiness_score = min(100, readiness_score + 10)

    recommendations: list[str] = []
    if missing_required:
        recommendations.append(f"Add projects demonstrating {', '.join(missing_required[:2])} before applying.")
    recommendations.append("Highlight quantifiable impact metrics in your experience bullet points.")

    cand_oid = PydanticObjectId(candidate_id)
    job_oid = PydanticObjectId(job_id)
    res_oid = PydanticObjectId(resume_id) if resume_id else (resume.id if resume else None)

    # Persist or update match evaluation record
    existing = await matching_repo.get_by_candidate_and_job(candidate_id, job_id)
    if existing:
        existing.match_score = match_score
        existing.matched_skills = matched_skills
        existing.missing_required_skills = missing_required
        existing.missing_optional_skills = missing_optional
        existing.strengths = strengths
        existing.weaknesses = weaknesses
        existing.application_readiness_score = readiness_score
        existing.recommendations = recommendations
        await existing.save()
        match_obj = existing
    else:
        match_obj = JobMatch(
            candidate_id=cand_oid,
            job_id=job_oid,
            resume_id=res_oid,
            match_score=match_score,
            matched_skills=matched_skills,
            missing_required_skills=missing_required,
            missing_optional_skills=missing_optional,
            strengths=strengths,
            weaknesses=weaknesses,
            application_readiness_score=readiness_score,
            recommendations=recommendations,
        )
        match_obj = await matching_repo.create(match_obj)

    logger.info("Job Match evaluated: Candidate %s vs Job %s (Score: %.1f%%)", candidate_id, job_id, match_score)
    return _build_match_response(match_obj)
