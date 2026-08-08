export interface InterviewQuestion {
  id: string;
  question_text: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  ideal_answer_benchmarks?: string[];
}

export interface TurnEvaluation {
  technical_correctness_score: number;
  communication_clarity_score: number;
  problem_solving_depth_score: number;
  behavioral_alignment_score: number;
  experience_relevance_score: number;
  overall_turn_score: number;
  key_strengths: string[];
  areas_for_improvement: string[];
  evaluation_reasoning: string;
}

export interface InterviewTurn {
  turn_index: number;
  question: InterviewQuestion;
  candidate_answer: string;
  evaluation: TurnEvaluation;
  created_at: string;
}

export interface InterviewReport {
  overall_score: number;
  total_turns: number;
  dimension_averages: Record<string, number>;
  key_strengths: string[];
  areas_for_improvement: string[];
  hiring_recommendation: string;
  summary_assessment: string;
}

export interface InterviewSession {
  id: string;
  candidate_id: string;
  job_id?: string;
  current_question_index: number;
  current_difficulty: "easy" | "medium" | "hard";
  max_questions: number;
  status: "in_progress" | "ready_to_complete" | "completed" | "abandoned";
  turns: InterviewTurn[];
  final_report?: InterviewReport;
  created_at: string;
}

export interface InterviewStartRequest {
  job_id?: string;
  difficulty?: "easy" | "medium" | "hard";
  max_questions?: number;
}

export interface TurnSubmitRequest {
  candidate_answer: string;
}
