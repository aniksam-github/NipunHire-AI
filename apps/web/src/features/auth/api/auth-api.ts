/**
 * Auth API layer — all HTTP calls for authentication.
 *
 * Each function maps 1:1 to a backend endpoint. They return typed
 * promises and throw AxiosErrors on failure. The hooks layer
 * (use-auth.ts) wraps these in React Query mutations/queries.
 *
 * No business logic here — just HTTP call + type annotation.
 */

import { api } from "@/shared/lib/axios";
import type { AuthResponse, TokenPair, User } from "@/shared/types/api";
import type { LoginFormData, RegisterPayload, RefreshPayload } from "../types";

/** POST /auth/register — create a new account */
export async function registerUser(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/register", payload);
  return data;
}

/** POST /auth/login — authenticate with email + password */
export async function loginUser(payload: LoginFormData): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", payload);
  return data;
}

/** POST /auth/refresh — exchange refresh token for new pair */
export async function refreshTokens(payload: RefreshPayload): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/auth/refresh", payload);
  return data;
}

/** GET /auth/me — fetch current user profile (requires valid access token) */
export async function getCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}
