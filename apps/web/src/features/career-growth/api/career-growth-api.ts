import { api } from "@/shared/lib/axios";
import type { CareerGoal, CareerProgress, InterviewSession, InterviewType } from "../types";

export const getGoals = async () => (await api.get<CareerGoal[]>("/goals")).data;
export const getProgress = async () => (await api.get<CareerProgress>("/progress/me")).data;
export const getInterviews = async () => (await api.get<InterviewSession[]>("/interviews")).data;

export const createGoal = async (payload: Pick<CareerGoal, "title" | "category" | "target_value" | "unit">) =>
  (await api.post<CareerGoal>("/goals", payload)).data;

export const updateGoalProgress = async (goal: CareerGoal, current_value: number) =>
  (await api.patch<CareerGoal>(`/goals/${goal.id}/progress`, { current_value })).data;

export const startInterview = async (payload: { interview_type: InterviewType; topic: string; question_count: number }) =>
  (await api.post<InterviewSession>("/interviews", payload)).data;

export const submitInterview = async (id: string, answers: string[]) =>
  (await api.post<InterviewSession>(`/interviews/${id}/submit`, { answers })).data;
