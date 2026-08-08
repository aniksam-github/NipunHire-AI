"""
Phase 9 Research Features Service — Explainability trace consolidation, deterministic consistency metrics,
statistical process bias auditing, resume internal consistency audit, and interview cheat risk detection.
"""

import json
import logging
import math
from typing import Any, Sequence

from beanie import PydanticObjectId

from app.ai.services.ai_service import AIService
from app.core.exceptions import EntityNotFoundError
from app.core.research_exceptions import AnomalyDetectionError, BiasAuditError, ExplanationTraceError
from app.models.research import (
    InterviewAnomalyItem,
    InterviewCheatRiskReport,
    ResumeAnomalyReport,
    ResumeInconsistencyItem,
)
from app.repositories import (
    coding_repo,
    interview_repo,
    job_repo,
    matching_repo,
    profile_repo,
    research_repo,
    resume_profile_repo,
    resume_repo,
)
from app.schemas.research import (
    ConsistencyMetrics,
    ExplanationTraceResponse,
    InterviewAnomalyFlag,
    InterviewCheatRiskResponse,
    ProcessBiasAuditResponse,
    ProcessPatternFlag,
    ResumeAnomalyCheckResponse,
    ResumeInconsistencyFlag,
    ScoreStatistics,
)
from app.services.prompt_service import load_prompt

logger = logging.getLogger(__name__)


# --- Module 1: Deterministic Consistency Metrics ---
def compute_consistency_metrics(
    match_score: float | None,
    interview_score: float | None,
    coding_score: float | None,
    has_coding_syntax_error: bool = False,
) -> ConsistencyMetrics:
    """
    Academic Methodology:
    Calculates deterministic cross-phase alignment metrics to flag pipeline anomalies.
    """
    scores = [s for s in (match_score, interview_score, coding_score) if s is not None]
    mismatches: list[str] = []

    if not scores:
        return ConsistencyMetrics(alignment_score=100.0, is_consistent=True, flagged_mismatches=[])

    if len(scores) == 1:
        return ConsistencyMetrics(alignment_score=100.0, is_consistent=True, flagged_mismatches=[])

    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    std_dev = math.sqrt(variance)

    # Alignment score decreases with standard deviation across phase scores
    alignment_score = max(0.0, round(100.0 - (std_dev * 2.0), 2))

    # Explicit rule-based logical mismatch checks
    if match_score is not None and interview_score is not None:
        if match_score >= 80.0 and interview_score <= 50.0:
            mismatches.append(f"High resume match ({match_score}%) conflicts with low interview performance ({interview_score}%).")
        elif match_score <= 50.0 and interview_score >= 85.0:
            mismatches.append(f"Low initial resume match ({match_score}%) conflicts with high interview performance ({interview_score}%).")

    if coding_score is not None and has_coding_syntax_error and coding_score >= 60.0:
        mismatches.append("Code review flagged syntax error, but coding score remains elevated.")

    is_consistent = len(mismatches) == 0 and alignment_score >= 70.0

    return ConsistencyMetrics(
        alignment_score=alignment_score,
        is_consistent=is_consistent,
        flagged_mismatches=mismatches,
    )


async def get_unified_explanation_trace(candidate_id: str, job_id: str) -> ExplanationTraceResponse:
    """Consolidates explainability outputs from Phase 4, Phase 6, and Phase 7 into a single trace."""
    match_doc = await matching_repo.get_by_candidate_and_job(candidate_id, job_id)
    sessions = await interview_repo.list_sessions_by_candidate(candidate_id, limit=5)
    target_session = next((s for s in sessions if str(s.job_id) == job_id), sessions[0] if sessions else None)

    submissions = await coding_repo.list_submissions_by_candidate(candidate_id, limit=5)
    target_sub = next((s for s in submissions if str(s.job_id) == job_id), submissions[0] if submissions else None)

    match_trace = match_doc.model_dump(mode="json") if match_doc else None
    interview_trace = target_session.model_dump(mode="json") if target_session else None
    coding_trace = target_sub.model_dump(mode="json") if target_sub else None

    m_score = float(match_doc.match_score) if match_doc and hasattr(match_doc, "match_score") else None
    i_score = float(target_session.overall_score) if target_session and target_session.overall_score is not None else None
    c_score = float(target_sub.overall_score) if target_sub and target_sub.overall_score is not None else None

    has_syntax_err = False
    if target_sub and target_sub.review and target_sub.review.is_incomplete_or_invalid:
        has_syntax_err = True

    metrics = compute_consistency_metrics(m_score, i_score, c_score, has_coding_syntax_error=has_syntax_err)

    return ExplanationTraceResponse(
        candidate_id=candidate_id,
        job_id=job_id,
        match_trace=match_trace,
        interview_trace=interview_trace,
        coding_trace=coding_trace,
        consistency_metrics=metrics,
    )


# --- Module 2: Statistical Process Bias Audit ---
def compute_statistical_process_audit(
    scores: Sequence[float],
    rejection_factor_counts: dict[str, int] | None = None,
) -> tuple[ScoreStatistics, list[ProcessPatternFlag], list[dict[str, Any]]]:
    """
    Academic Methodology:
    Pure deterministic statistical analysis auditing evaluation variance and factor dominance across an applicant pool.
    Contains ZERO demographic attribute collection or profiling.
    """
    if not scores:
        stats = ScoreStatistics(mean=0.0, median=0.0, std_dev=0.0, min_score=0.0, max_score=0.0)
        return stats, [], []

    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    mean_val = round(sum(sorted_scores) / n, 2)
    median_val = round(sorted_scores[n // 2] if n % 2 != 0 else (sorted_scores[(n // 2) - 1] + sorted_scores[n // 2]) / 2.0, 2)
    min_val = round(sorted_scores[0], 2)
    max_val = round(sorted_scores[-1], 2)

    variance = sum((x - mean_val) ** 2 for x in sorted_scores) / n
    std_dev_val = round(math.sqrt(variance), 2)

    stats = ScoreStatistics(
        mean=mean_val,
        median=median_val,
        std_dev=std_dev_val,
        min_score=min_val,
        max_score=max_val,
    )

    flags: list[ProcessPatternFlag] = []

    if std_dev_val > 22.0:
        flags.append(
            ProcessPatternFlag(
                pattern_name="High Variance in Applicant Pool",
                description="The standard deviation across applicant scores is unusually high (>22.0), suggesting potential inconsistency in scoring factors.",
                severity="warning",
                statistic_summary=f"Std Dev = {std_dev_val}, Min = {min_val}, Max = {max_val}",
            )
        )

    if (mean_val - median_val) > 15.0:
        flags.append(
            ProcessPatternFlag(
                pattern_name="Right-Skewed Distribution",
                description="Mean score significantly exceeds median score, indicating a small subset of high outliers driving pool metrics.",
                severity="info",
                statistic_summary=f"Mean = {mean_val}, Median = {median_val}",
            )
        )

    dominant_factors: list[dict[str, Any]] = []
    if rejection_factor_counts:
        total_rejections = sum(rejection_factor_counts.values())
        if total_rejections > 0:
            for factor, count in sorted(rejection_factor_counts.items(), key=lambda x: x[1], reverse=True):
                pct = round((count / total_rejections) * 100.0, 1)
                dominant_factors.append({"factor_name": factor, "rejection_impact_percentage": pct})
                if pct >= 50.0:
                    flags.append(
                        ProcessPatternFlag(
                            pattern_name="Single Factor Rejection Dominance",
                            description=f"Factor '{factor}' disproportionately accounts for {pct}% of all negative points across the candidate pool.",
                            severity="warning",
                            statistic_summary=f"Factor impact = {pct}%",
                        )
                    )

    return stats, flags, dominant_factors


async def audit_job_scoring_process(job_id: str) -> ProcessBiasAuditResponse:
    """Audits scoring process variance across all applicants for a given job."""
    matches = await matching_repo.list_recent_by_candidate("", limit=100)
    job_matches = [m for m in matches if str(m.job_id) == job_id]

    scores: list[float] = []
    factor_counts: dict[str, int] = {}

    for m in job_matches:
        if hasattr(m, "match_score") and m.match_score is not None:
            scores.append(float(m.match_score))
        if hasattr(m, "explainable_result") and m.explainable_result:
            missing = getattr(m.explainable_result, "missing_skills", []) or []
            for skill in missing:
                factor_counts[skill] = factor_counts.get(skill, 0) + 1

    stats, flags, dominant_factors = compute_statistical_process_audit(scores, factor_counts)

    return ProcessBiasAuditResponse(
        job_id=job_id,
        total_applicants_audited=len(scores),
        score_statistics=stats,
        flagged_process_patterns=flags,
        dominant_rejection_factors=dominant_factors,
    )


# --- Module 3: Resume Internal Consistency Audit ---
async def check_resume_anomalies(
    candidate_id: str,
    resume_id: str,
    ai_service: AIService | None = None,
) -> ResumeAnomalyCheckResponse:
    """Audits stated resume text for internal contradictions (overlapping dates, unsupported skills)."""
    ai = ai_service or AIService()
    resume_text = "Resume Content"

    try:
        resume = await resume_repo.get_by_id(resume_id)
        if resume and hasattr(resume, "raw_text") and resume.raw_text:
            resume_text = resume.raw_text[:10_000]
        else:
            resume_prof = await resume_profile_repo.get_by_resume_id(resume_id)
            if resume_prof:
                resume_text = json.dumps(resume_prof.model_dump(mode="json"))
    except Exception as exc:
        logger.warning("Could not fetch raw resume text for %s: %s", resume_id, exc)

    prompt = load_prompt("resume_fraud_check", resume_content=resume_text)

    try:
        response = await ai.get_structured_response(
            system_prompt="You are an expert resume consistency auditor.",
            user_prompt=prompt,
            response_model=ResumeAnomalyCheckResponse,
        )
        response.resume_id = resume_id
        response.candidate_id = candidate_id

        # Persist report in MongoDB
        items = [
            ResumeInconsistencyItem(
                issue_type=flag.issue_type,
                description=flag.description,
                confidence_level=flag.confidence_level,
                supporting_evidence=flag.supporting_evidence,
            )
            for flag in response.flagged_inconsistencies
        ]
        db_report = ResumeAnomalyReport(
            resume_id=PydanticObjectId(resume_id),
            candidate_id=PydanticObjectId(candidate_id),
            overall_risk_score=response.overall_risk_score,
            flagged_inconsistencies=items,
            requires_human_review=response.requires_human_review,
            human_review_disclaimer=response.human_review_disclaimer,
        )
        await research_repo.create_resume_anomaly_report(db_report)
        return response
    except Exception as exc:
        logger.error("Failed to perform resume anomaly audit: %s", exc)
        raise AnomalyDetectionError("Failed to perform resume anomaly audit via AI") from exc


# --- Module 4: Interview Cheat Risk Detection ---
async def detect_interview_cheat_risk(
    candidate_id: str,
    session_id: str,
    ai_service: AIService | None = None,
) -> InterviewCheatRiskResponse:
    """Analyzes stored interview Q&A history for stylometric anomalies (phrasing shifts, unnatural polish)."""
    ai = ai_service or AIService()
    session = await interview_repo.get_session_by_id(session_id)
    if not session:
        raise EntityNotFoundError(entity="Interview Session", identifier=session_id)

    turns_data = []
    for turn in session.turns:
        turns_data.append({
            "turn_index": turn.turn_index,
            "question": turn.question.question_text,
            "difficulty": turn.question.difficulty.value,
            "answer": turn.candidate_answer,
            "turn_score": turn.evaluation.overall_turn_score,
        })

    prompt = load_prompt("interview_cheat_risk", interview_history_json=json.dumps(turns_data))

    try:
        response = await ai.get_structured_response(
            system_prompt="You are a stylometric analysis expert auditing interview responses.",
            user_prompt=prompt,
            response_model=InterviewCheatRiskResponse,
        )
        response.session_id = session_id
        response.candidate_id = candidate_id

        # Persist report in MongoDB
        items = [
            InterviewAnomalyItem(
                anomaly_type=flag.anomaly_type,
                turn_index=flag.turn_index,
                description=flag.description,
                confidence_level=flag.confidence_level,
            )
            for flag in response.flagged_anomalies
        ]
        db_report = InterviewCheatRiskReport(
            session_id=PydanticObjectId(session_id),
            candidate_id=PydanticObjectId(candidate_id),
            cheat_risk_score=response.cheat_risk_score,
            risk_level=response.risk_level,
            flagged_anomalies=items,
            supporting_reasoning=response.supporting_reasoning,
            is_informational_only=response.is_informational_only,
            human_review_disclaimer=response.human_review_disclaimer,
        )
        await research_repo.create_interview_cheat_report(db_report)
        return response
    except Exception as exc:
        logger.error("Failed to perform interview cheat risk detection: %s", exc)
        raise AnomalyDetectionError("Failed to run interview cheat risk detection via AI") from exc
