import type { InterviewReport } from "./interview";

export interface CandidateSummaryReport {
  candidate_id: string;
  key_highlights: string[];
  overall_assessment: string;
  standout_signals: Record<string, string[]>;
  available_data_sources: string[];
}

export interface CandidateComparisonRequest {
  job_id: string;
  candidate_ids: string[];
}

export interface CandidateComparisonEntry {
  candidate_id: string;
  full_name?: string;
  relative_strengths: string[];
  dimension_ratings: Record<string, number>;
}

export interface CandidateComparisonResult {
  job_id: string;
  candidates_compared: string[];
  per_candidate_breakdown: CandidateComparisonEntry[];
  dimension_leaders: Record<string, string>;
  comparison_summary: string;
}

export interface RankingWeights {
  match_weight: number;
  interview_weight: number;
  coding_weight: number;
}

export interface RankedCandidateEntry {
  rank: number;
  candidate_id: string;
  composite_score: number;
  sub_scores: Record<string, number | null>;
  justification: string;
}

export interface CandidateRankingList {
  job_id: string;
  weights_used: RankingWeights;
  rankings: RankedCandidateEntry[];
}

export interface RecruiterInterviewHighlight {
  turn_index: number;
  question_text: string;
  category: string;
  candidate_answer_summary: string;
  turn_score: number;
}

export interface RecruiterInterviewSummaryResponse {
  session_id: string;
  candidate_id: string;
  job_id?: string;
  overall_score?: number;
  hiring_recommendation?: string;
  status: string;
  key_qa_highlights: RecruiterInterviewHighlight[];
  final_report?: InterviewReport;
}

export interface AggregateHiringRecommendationResponse {
  candidate_id: string;
  job_id?: string;
  recommendation: "Hire" | "Maybe" | "Reject";
  confidence_score: number;
  grounded_reason: string;
  key_factors: string[];
}

export interface JobDescriptionGenerateRequest {
  role_title: string;
  required_skills: string[];
  seniority_level: string;
}

export interface GeneratedJobDescription {
  role_title: string;
  seniority_level: string;
  summary: string;
  responsibilities: string[];
  required_qualifications: string[];
  preferred_qualifications: string[];
}
