export interface ConsistencyMetrics {
  alignment_score: number;
  is_consistent: boolean;
  flagged_mismatches: string[];
}

export interface ExplanationTraceResponse {
  candidate_id: string;
  job_id: string;
  match_trace?: Record<string, unknown>;
  interview_trace?: Record<string, unknown>;
  coding_trace?: Record<string, unknown>;
  consistency_metrics: ConsistencyMetrics;
  human_review_disclaimer: string;
}

export interface ScoreStatistics {
  mean: number;
  median: number;
  std_dev: number;
  min_score: number;
  max_score: number;
}

export interface ProcessPatternFlag {
  pattern_name: string;
  description: string;
  severity: "info" | "warning" | "critical";
  statistic_summary: string;
}

export interface ProcessBiasAuditResponse {
  job_id: string;
  total_applicants_audited: number;
  score_statistics: ScoreStatistics;
  flagged_process_patterns: ProcessPatternFlag[];
  dominant_rejection_factors: Array<{ factor_name: string; rejection_impact_percentage: number }>;
  human_review_disclaimer: string;
}

export interface ResumeInconsistencyFlag {
  issue_type: string;
  description: string;
  confidence_level: "low" | "medium" | "high";
  supporting_evidence?: string;
}

export interface ResumeAnomalyCheckResponse {
  resume_id: string;
  candidate_id: string;
  overall_risk_score: number;
  flagged_inconsistencies: ResumeInconsistencyFlag[];
  requires_human_review: boolean;
  human_review_disclaimer: string;
}

export interface InterviewAnomalyFlag {
  anomaly_type: string;
  turn_index: number;
  description: string;
  confidence_level: "low" | "medium" | "high";
}

export interface InterviewCheatRiskResponse {
  session_id: string;
  candidate_id: string;
  cheat_risk_score: number;
  risk_level: "low" | "moderate" | "high";
  flagged_anomalies: InterviewAnomalyFlag[];
  supporting_reasoning: string;
  is_informational_only: boolean;
  human_review_disclaimer: string;
}
