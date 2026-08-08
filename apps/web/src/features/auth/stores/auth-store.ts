/**
 * Auth Zustand store — client-side auth state.
 *
 * Holds: user profile, access token, refresh token, loading state.
 *
 * Why Zustand?
 *   1. Works outside React (Axios interceptors read tokens via getState)
 *   2. No re-render storms — components subscribe to specific slices
 *   3. Zero boilerplate — no reducers, no dispatch, no context wrapping
 *
 * Token storage strategy:
 *   Both tokens in memory (Zustand). On page refresh, user re-authenticates.
 *   This is MORE secure than localStorage — XSS can't steal in-memory tokens.
 *   Trade-off: no "remember me" (requires httpOnly cookie on the backend).
 */

import { create } from "zustand";
import type { User, TokenPair } from "@/shared/types/api";
import { registerAuthAccessor } from "@/shared/lib/axios";

interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  // Actions
  setAuth: (user: User, tokens: TokenPair) => void;
  setTokens: (tokens: TokenPair) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  // Initial state — unauthenticated
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,

  setAuth: (user, tokens) =>
    set({
      user,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      isAuthenticated: true,
    }),

  setTokens: (tokens) =>
    set({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
    }),

  setUser: (user) => set({ user }),

  logout: () =>
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    }),
}));

// ---------------------------------------------------------------------------
// Register with Axios interceptors (breaks circular dependency)
// ---------------------------------------------------------------------------
registerAuthAccessor({
  getAccessToken: () => useAuthStore.getState().accessToken,
  getRefreshToken: () => useAuthStore.getState().refreshToken,
  setTokens: (tokens) => useAuthStore.getState().setTokens(tokens),
  logout: () => useAuthStore.getState().logout(),
});
