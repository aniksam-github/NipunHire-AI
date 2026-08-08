export type InterviewType = "technical" | "hr" | "behavioral" | "company_specific";

export interface InterviewSession {
  id: string;
  interview_type: InterviewType;
  topic: string;
  company: string | null;
  position: string | null;
  questions: string[];
  answers: string[];
  feedback: string[];
  overall_score: number | null;
  completed_at: string | null;
  created_at: string;
}

export interface CareerGoal {
  id: string;
  title: string;
  category: "interview" | "skill" | "coding" | "career";
  target_value: number;
  current_value: number;
  unit: string;
  due_date: string | null;
  status: "active" | "completed" | "paused";
  created_at: string;
  updated_at: string;
}

export interface CareerProgress {
  active_goals: number;
  completed_goals: number;
  completed_interviews: number;
  interview_average_score: number | null;
  achievements: string[];
}
