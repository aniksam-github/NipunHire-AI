/**
 * Generic API response/error types matching the FastAPI backend's response shape.
 *
 * These are used across all features — every API call returns data
 * in one of these shapes, so we type them once here rather than
 * re-defining per feature.
 */

/** Standard error detail returned by FastAPI's HTTPException */
export interface ApiErrorResponse {
  detail: string;
}

/** Pydantic validation error shape (422 responses) */
export interface ValidationErrorItem {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ValidationErrorResponse {
  detail: ValidationErrorItem[];
}

/**
 * User roles — kept in sync with backend's UserRole enum.
 * Using a const object + type union instead of TS enum because:
 *   - TS enums emit runtime JS code
 *   - const objects are tree-shakeable
 *   - Type unions give better DX in discriminated unions
 */
export const USER_ROLES = {
  RECRUITER: "recruiter",
  CANDIDATE: "candidate",
  ADMIN: "admin",
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

/** User profile — matches backend's UserResponse schema */
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

/** Token pair — matches backend's TokenResponse schema */
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** Combined auth response — matches backend's AuthResponse schema */
export interface AuthResponse {
  user: User;
  tokens: TokenPair;
}
