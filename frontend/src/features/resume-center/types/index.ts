/**
 * Resume Center feature types.
 */

export interface QualityBreakdown {
  completeness_score: number;
  keyword_density_score: number;
  formatting_score: number;
}

export interface AIFeedback {
  missing_elements: string[];
  action_verb_suggestions: string[];
  formatting_tips: string[];
}

export interface Resume {
  id: string;
  candidate_id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  parsed_name?: string;
  parsed_email?: string;
  parsed_phone?: string;
  extracted_skills: string[];
  ats_score: number;
  quality_breakdown: QualityBreakdown;
  ai_feedback: AIFeedback;
  is_primary: boolean;
  created_at: string;
}
