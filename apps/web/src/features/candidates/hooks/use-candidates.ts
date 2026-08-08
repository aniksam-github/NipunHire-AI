/**
 * Candidates React Query hooks for AI job matching evaluations.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { type AxiosError } from "axios";

import { compareJobMatch } from "../api/candidates-api";
import type { MatchRequest, MatchResponse } from "../types";
import type { ApiErrorResponse } from "@/shared/types/api";

export function useCompareJobMatch() {
  const queryClient = useQueryClient();

  return useMutation<MatchResponse, AxiosError<ApiErrorResponse>, MatchRequest>({
    mutationFn: (payload: MatchRequest) => compareJobMatch(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["matches"] });
      toast.success(`AI Match Evaluation Complete! Score: ${data.match_score}%`);
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const msg = error.response?.data?.detail ?? "Failed to run job match evaluation.";
      toast.error(msg);
    },
  });
}
