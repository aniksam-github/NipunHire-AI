"""Aggregates persisted candidate career data for the dashboard."""

from beanie import PydanticObjectId

from app.models.application import Application, ApplicationStatus
from app.models.matching import JobMatch
from app.models.resume import Resume
from app.schemas.dashboard import (
    ApplicationStatusSummary,
    CandidateDashboardResponse,
    RecentApplication,
)
from app.services.profile_service import get_or_create_profile


async def get_candidate_dashboard(candidate_id: str) -> CandidateDashboardResponse:
    """Build a dashboard from the authenticated candidate's stored records."""
    profile = await get_or_create_profile(candidate_id)
    candidate_oid = PydanticObjectId(candidate_id)
    applications = await Application.find(
        Application.candidate_id == candidate_oid
    ).sort("-updated_at").to_list()
    resumes = await Resume.find(Resume.candidate_id == candidate_oid).sort("-created_at").to_list()
    matches = await JobMatch.find(JobMatch.candidate_id == candidate_oid).sort("-created_at").to_list()

    status_counts = {status: 0 for status in ApplicationStatus}
    for application in applications:
        status_counts[application.status] += 1

    summary = ApplicationStatusSummary(
        saved=status_counts[ApplicationStatus.SAVED],
        applied=status_counts[ApplicationStatus.APPLIED],
        shortlisted=status_counts[ApplicationStatus.SHORTLISTED],
        interview_scheduled=status_counts[ApplicationStatus.INTERVIEW_SCHEDULED],
        offer_received=status_counts[ApplicationStatus.OFFER_RECEIVED],
        rejected=status_counts[ApplicationStatus.REJECTED],
    )
    primary_resume = next((resume for resume in resumes if resume.is_primary), None)
    resume_health_score = primary_resume.ats_score if primary_resume else None

    recommendations: list[str] = []
    if profile.completion_percentage < 80:
        recommendations.append("Complete your profile to improve job-match recommendations.")
    if not primary_resume:
        recommendations.append("Upload a resume to receive an ATS health score and tailored feedback.")
    elif primary_resume.ats_score < 80:
        recommendations.append("Improve your primary resume using the ATS recommendations before applying.")
    if not applications:
        recommendations.append("Save or apply to a role to begin tracking your job-search progress.")

    missing_skills: list[str] = []
    for match in matches:
        for skill in match.missing_required_skills:
            if skill not in missing_skills:
                missing_skills.append(skill)
    skill_suggestions = [
        f"Build or revise a project that demonstrates {skill}."
        for skill in missing_skills[:3]
    ]

    return CandidateDashboardResponse(
        profile_completion_percentage=profile.completion_percentage,
        resume_health_score=resume_health_score,
        application_summary=summary,
        upcoming_interviews=summary.interview_scheduled,
        recent_applications=[
            RecentApplication(
                id=str(application.id),
                job_id=str(application.job_id),
                status=application.status,
                updated_at=application.updated_at,
            )
            for application in applications[:5]
        ],
        daily_recommendations=recommendations,
        skill_improvement_suggestions=skill_suggestions,
        weekly_progress={
            "applications_updated": len(applications),
            "resumes_uploaded": len(resumes),
            "job_matches_evaluated": len(matches),
        },
    )
