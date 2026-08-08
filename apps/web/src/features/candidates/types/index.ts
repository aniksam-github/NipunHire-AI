/**
 * Candidates feature types — matching request, evaluation response, and candidate models.
 */

export interface MatchRequest {
  job_id: string;
  resume_id?: string;
}

export interface MatchResponse {
  id: string;
  candidate_id: string;
  job_id: string;
  resume_id?: string;
  match_score: number;
  matched_skills: string[];
  missing_required_skills: string[];
  missing_optional_skills: string[];
  strengths: string[];
  weaknesses: string[];
  application_readiness_score: number;
  recommendations: string[];
}
