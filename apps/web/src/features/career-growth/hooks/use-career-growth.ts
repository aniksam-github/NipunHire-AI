import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createGoal, getGoals, getInterviews, getProgress, startInterview, submitInterview, updateGoalProgress } from "../api/career-growth-api";
import type { CareerGoal } from "../types";

export const useCareerProgress = () => useQuery({ queryKey: ["career-progress"], queryFn: getProgress });
export const useGoals = () => useQuery({ queryKey: ["career-goals"], queryFn: getGoals });
export const useInterviews = () => useQuery({ queryKey: ["interviews"], queryFn: getInterviews });

export function useCareerActions() {
  const queryClient = useQueryClient();
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["career-progress"] });
  const refreshGoals = () => { refresh(); return queryClient.invalidateQueries({ queryKey: ["career-goals"] }); };
  return {
    createGoal: useMutation({ mutationFn: createGoal, onSuccess: refreshGoals }),
    updateGoal: useMutation({ mutationFn: ({ goal, value }: { goal: CareerGoal; value: number }) => updateGoalProgress(goal, value), onSuccess: refreshGoals }),
    startInterview: useMutation({ mutationFn: startInterview, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["interviews"] }) }),
    submitInterview: useMutation({ mutationFn: ({ id, answers }: { id: string; answers: string[] }) => submitInterview(id, answers), onSuccess: () => { refresh(); queryClient.invalidateQueries({ queryKey: ["interviews"] }); } }),
  };
}
