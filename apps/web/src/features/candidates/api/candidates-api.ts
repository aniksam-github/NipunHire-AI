/**
 * Candidates API layer — HTTP calls for matching and screening evaluations.
 */

import { api } from "@/shared/lib/axios";
import type { MatchRequest, MatchResponse } from "../types";

/** POST /matching/compare — Evaluates job match for candidate/resume vs job specification */
export async function compareJobMatch(payload: MatchRequest): Promise<MatchResponse> {
  const { data } = await api.post<MatchResponse>("/matching/compare", payload);
  return data;
}
