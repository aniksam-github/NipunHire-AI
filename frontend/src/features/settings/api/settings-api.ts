/**
 * Settings & Profile API layer — HTTP calls for user profile management.
 */

import { api } from "@/shared/lib/axios";
import type { ProfileResponse, ProfileUpdate } from "../types";

/** GET /profile/me — Get current user candidate profile */
export async function getProfile(): Promise<ProfileResponse> {
  const { data } = await api.get<ProfileResponse>("/profile/me");
  return data;
}

/** PUT /profile/me — Update current user candidate profile */
export async function updateProfile(payload: ProfileUpdate): Promise<ProfileResponse> {
  const { data } = await api.put<ProfileResponse>("/profile/me", payload);
  return data;
}
