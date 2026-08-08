import { api } from "@/shared/lib/axios";

export interface CandidateDashboard {
  profile_completion_percentage: number;
  resume_health_score: number | null;
  application_summary: Record<string, number>;
  upcoming_interviews: number;
  daily_recommendations: string[];
  skill_improvement_suggestions: string[];
  weekly_progress: Record<string, number>;
}

export async function getCandidateDashboard(): Promise<CandidateDashboard> {
  return (await api.get<CandidateDashboard>("/dashboard/me")).data;
}
