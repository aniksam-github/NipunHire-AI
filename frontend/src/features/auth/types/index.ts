/**
 * Auth feature types — request payloads and form schemas.
 *
 * These are feature-local types. Shared response types (User, TokenPair,
 * AuthResponse) live in shared/types/api.ts. Feature types handle
 * what the UI sends, shared types handle what the API returns.
 */

import { z } from "zod";

// ---------------------------------------------------------------------------
// Zod schemas — single source of truth for form + API validation
// ---------------------------------------------------------------------------

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(1, "Password is required"),
});

export const registerSchema = z.object({
  full_name: z
    .string()
    .min(1, "Full name is required")
    .max(100, "Name must be under 100 characters"),
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password must be under 128 characters"),
  confirm_password: z
    .string()
    .min(1, "Please confirm your password"),
  role: z.enum(["recruiter", "candidate"]),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

// ---------------------------------------------------------------------------
// Inferred types — derived from Zod schemas, not manually defined
// ---------------------------------------------------------------------------

/** Form data shape for login */
export type LoginFormData = z.infer<typeof loginSchema>;

/** Form data shape for registration */
export type RegisterFormData = z.infer<typeof registerSchema>;

/** What we actually send to the API (no confirm_password) */
export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role: "recruiter" | "candidate";
}

/** What we send for token refresh */
export interface RefreshPayload {
  refresh_token: string;
}
