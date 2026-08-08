import { api } from "./axios";

import type {
  InterviewStartRequest,
  InterviewSession,
  TurnSubmitRequest,
  InterviewTurn,
  InterviewReport,
} from "../types/interview";

import type {
  CodingQuestionGenerateRequest,
  CodingQuestionGenerateResponse,
  CodingSubmissionCreate,
  ConsolidatedCodingFeedbackResponse,
} from "../types/coding";

import type {
  CandidateSummaryReport,
  CandidateComparisonRequest,
  CandidateComparisonResult,
  CandidateRankingList,
  RankingWeights,
  RecruiterInterviewSummaryResponse,
  AggregateHiringRecommendationResponse,
  JobDescriptionGenerateRequest,
  GeneratedJobDescription,
} from "../types/recruiter";

import type {
  ExplanationTraceResponse,
  ProcessBiasAuditResponse,
  ResumeAnomalyCheckResponse,
  InterviewCheatRiskResponse,
} from "../types/research";

// --- Phase 6 Interview AI API ---
export const interviewApi = {
  startSession: async (data: InterviewStartRequest): Promise<InterviewSession> => {
    const res = await api.post<InterviewSession>("/interviews/sessions/start", data);
    return res.data;
  },
  submitTurn: async (sessionId: string, data: TurnSubmitRequest): Promise<InterviewTurn> => {
    const res = await api.post<InterviewTurn>(`/interviews/sessions/${sessionId}/turn`, data);
    return res.data;
  },
  getSession: async (sessionId: string): Promise<InterviewSession> => {
    const res = await api.get<InterviewSession>(`/interviews/sessions/${sessionId}`);
    return res.data;
  },
  completeSession: async (sessionId: string): Promise<InterviewReport> => {
    const res = await api.post<InterviewReport>(`/interviews/sessions/${sessionId}/complete`);
    return res.data;
  },
  getReport: async (sessionId: string): Promise<InterviewReport> => {
    const res = await api.get<InterviewReport>(`/interviews/sessions/${sessionId}/report`);
    return res.data;
  },
};

// --- Phase 7 Coding AI API ---
export const codingApi = {
  generateQuestion: async (data: CodingQuestionGenerateRequest): Promise<CodingQuestionGenerateResponse> => {
    const res = await api.post<CodingQuestionGenerateResponse>("/coding/questions/generate", data);
    return res.data;
  },
  submitCodeForReview: async (data: CodingSubmissionCreate): Promise<ConsolidatedCodingFeedbackResponse> => {
    const res = await api.post<ConsolidatedCodingFeedbackResponse>("/coding/submissions/review", data);
    return res.data;
  },
  getConsolidatedFeedback: async (submissionId: string): Promise<ConsolidatedCodingFeedbackResponse> => {
    const res = await api.get<ConsolidatedCodingFeedbackResponse>(`/coding/submissions/${submissionId}`);
    return res.data;
  },
};

// --- Phase 8 Recruiter AI API ---
export const recruiterApi = {
  getCandidateSummary: async (candidateId: string, jobId?: string): Promise<CandidateSummaryReport> => {
    const res = await api.post<CandidateSummaryReport>("/recruiter/candidate-summary", null, {
      params: { candidate_id: candidateId, job_id: jobId },
    });
    return res.data;
  },
  compareCandidates: async (data: CandidateComparisonRequest): Promise<CandidateComparisonResult> => {
    const res = await api.post<CandidateComparisonResult>("/recruiter/candidates/compare", data);
    return res.data;
  },
  rankCandidates: async (jobId: string, candidateIds?: string[], weights?: RankingWeights): Promise<CandidateRankingList> => {
    const res = await api.post<CandidateRankingList>(`/recruiter/jobs/${jobId}/rankings`, {
      candidate_ids: candidateIds,
      weights,
    });
    return res.data;
  },
  getInterviewSummary: async (sessionId: string): Promise<RecruiterInterviewSummaryResponse> => {
    const res = await api.get<RecruiterInterviewSummaryResponse>(`/recruiter/interviews/${sessionId}/summary`);
    return res.data;
  },
  getAggregateRecommendation: async (candidateId: string, jobId?: string): Promise<AggregateHiringRecommendationResponse> => {
    const res = await api.post<AggregateHiringRecommendationResponse>("/recruiter/recommendation", {
      candidate_id: candidateId,
      job_id: jobId,
    });
    return res.data;
  },
  generateJobDescription: async (data: JobDescriptionGenerateRequest): Promise<GeneratedJobDescription> => {
    const res = await api.post<GeneratedJobDescription>("/recruiter/job-description/generate", data);
    return res.data;
  },
};

// --- Phase 9 Research Features API ---
export const researchApi = {
  getExplanationTrace: async (candidateId: string, jobId: string): Promise<ExplanationTraceResponse> => {
    const res = await api.get<ExplanationTraceResponse>("/research/explanation-trace", {
      params: { candidate_id: candidateId, job_id: jobId },
    });
    return res.data;
  },
  auditProcessBias: async (jobId: string): Promise<ProcessBiasAuditResponse> => {
    const res = await api.get<ProcessBiasAuditResponse>(`/research/bias-audit/${jobId}`);
    return res.data;
  },
  checkResumeAnomalies: async (candidateId: string, resumeId: string): Promise<ResumeAnomalyCheckResponse> => {
    const res = await api.post<ResumeAnomalyCheckResponse>("/research/resume-anomaly-check", null, {
      params: { candidate_id: candidateId, resume_id: resumeId },
    });
    return res.data;
  },
  detectCheatRisk: async (candidateId: string, sessionId: string): Promise<InterviewCheatRiskResponse> => {
    const res = await api.post<InterviewCheatRiskResponse>("/research/interview-cheat-risk", null, {
      params: { candidate_id: candidateId, session_id: sessionId },
    });
    return res.data;
  },
};
