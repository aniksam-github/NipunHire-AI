export interface CodingExample {
  input: string;
  output: string;
  explanation?: string;
}

export interface CodingQuestion {
  id: string;
  title: string;
  problem_statement: string;
  input_output_format?: string;
  examples?: CodingExample[];
  constraints?: string[];
  difficulty: "easy" | "medium" | "hard";
  topics?: string[];
  starter_code?: string;
}

export interface CodingQuestionGenerateRequest {
  job_id: string;
  difficulty?: "easy" | "medium" | "hard";
}

export interface CodingQuestionGenerateResponse {
  question: CodingQuestion;
  job_id: string;
  candidate_id: string;
  created_at: string;
}

export interface CodingSubmissionCreate {
  question_id: string;
  language: "python" | "javascript" | "typescript" | "java" | "cpp" | "sql" | "go";
  code: string;
}

export interface CodingReviewResult {
  correctness_score: number;
  code_quality_score: number;
  overall_score: number;
  correctness_assessment: string;
  is_incomplete_or_invalid: boolean;
  identified_bugs: string[];
  time_complexity: string;
  space_complexity: string;
  complexity_explanation: string;
  code_quality_observations: string[];
  optimization_suggestions: string[];
}

export interface ConsolidatedCodingFeedbackResponse {
  submission_id: string;
  candidate_id: string;
  job_id?: string;
  question: CodingQuestion;
  language: string;
  submitted_code: string;
  submitted_at: string;
  review: CodingReviewResult;
}
