/**
 * Auth hooks — React Query wrappers around auth API calls.
 *
 * Each hook encapsulates:
 *   - the API call (via auth-api.ts)
 *   - loading/error/success state (via React Query)
 *   - side effects on success (update Zustand store, navigate, toast)
 *
 * Components call these hooks — they never call the API layer
 * or the store directly. This keeps components focused on rendering.
 */

import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { type AxiosError } from "axios";
import { toast } from "sonner";

import { useAuthStore } from "../stores/auth-store";
import { loginUser, registerUser, getCurrentUser } from "../api/auth-api";
import type { RegisterFormData, RegisterPayload } from "../types";
import type { ApiErrorResponse } from "@/shared/types/api";

/**
 * useLogin — handles the login flow end-to-end.
 *
 * On success: stores user + tokens, navigates to /dashboard, shows toast.
 * On error: returns error message for the form to display.
 */
export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      setAuth(data.user, data.tokens);
      toast.success(`Welcome back, ${data.user.full_name}!`);
      navigate("/dashboard", { replace: true });
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const message =
        error.response?.data?.detail ?? "Login failed. Please try again.";
      toast.error(message);
    },
  });
}

/**
 * useRegister — handles the registration flow.
 *
 * Transforms RegisterFormData (with confirm_password) into
 * RegisterPayload (without) before sending to the API.
 */
export function useRegister() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (formData: RegisterFormData) => {
      // Strip confirm_password — backend doesn't expect it
      const payload: RegisterPayload = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role,
      };
      return registerUser(payload);
    },
    onSuccess: (data) => {
      setAuth(data.user, data.tokens);
      toast.success("Account created successfully!");
      navigate("/dashboard", { replace: true });
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const message =
        error.response?.data?.detail ?? "Registration failed. Please try again.";
      toast.error(message);
    },
  });
}

/**
 * useCurrentUser — fetches the authenticated user's profile.
 *
 * Only runs when there's an access token in the store (enabled flag).
 * Used by the ProtectedRoute to verify the token is still valid.
 */
export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: getCurrentUser,
    enabled: !!accessToken,
    retry: false, // Don't retry — the interceptor handles refresh
    staleTime: 10 * 60 * 1000, // 10 minutes — user profile rarely changes
    select: (data) => {
      setUser(data);
      return data;
    },
    meta: {
      onError: () => {
        // If /me fails even after token refresh, log out
        logout();
      },
    },
  });
}

/**
 * useLogout — clears auth state and navigates to login.
 */
export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return () => {
    logout();
    toast.info("You have been logged out.");
    navigate("/login", { replace: true });
  };
}
