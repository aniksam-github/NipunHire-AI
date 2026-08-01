"""
Research Repository — database operations for ResumeAnomalyReport and InterviewCheatRiskReport Beanie documents.
"""

from typing import Optional
from beanie import PydanticObjectId

from app.models.research import InterviewCheatRiskReport, ResumeAnomalyReport


async def create_resume_anomaly_report(report: ResumeAnomalyReport) -> ResumeAnomalyReport:
    """Inserts a new ResumeAnomalyReport document into MongoDB."""
    return await report.insert()


async def get_resume_anomaly_report_by_resume_id(resume_id: str) -> Optional[ResumeAnomalyReport]:
    """Fetches the latest ResumeAnomalyReport for a given resume_id."""
    try:
        r_oid = PydanticObjectId(resume_id)
        return await ResumeAnomalyReport.find_one(
            ResumeAnomalyReport.resume_id == r_oid,
        ).sort("-created_at")
    except Exception:
        return None


async def create_interview_cheat_report(report: InterviewCheatRiskReport) -> InterviewCheatRiskReport:
    """Inserts a new InterviewCheatRiskReport document into MongoDB."""
    return await report.insert()


async def get_interview_cheat_report_by_session_id(session_id: str) -> Optional[InterviewCheatRiskReport]:
    """Fetches the latest InterviewCheatRiskReport for a given session_id."""
    try:
        s_oid = PydanticObjectId(session_id)
        return await InterviewCheatRiskReport.find_one(
            InterviewCheatRiskReport.session_id == s_oid,
        ).sort("-created_at")
    except Exception:
        return None
