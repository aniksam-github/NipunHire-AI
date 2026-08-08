/**
 * Centralized Axios instance with auth interceptors.
 *
 * Every API call in the app goes through this instance. It handles:
 *
 * 1. REQUEST INTERCEPTOR — auto-attaches the Bearer token from the
 *    auth store to every outgoing request. No component ever manually
 *    sets the Authorization header.
 *
 * 2. RESPONSE INTERCEPTOR — catches 401 responses, attempts a silent
 *    token refresh using the stored refresh token, and retries the
 *    original request. If refresh also fails, the user is logged out.
 *
 * Why Zustand here (not Context)?
 *   This file runs outside the React tree — there's no component,
 *   no hook, no JSX. Context can't be accessed here. Zustand's
 *   getState()/setState() work anywhere in plain JS/TS.
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import type { ApiErrorResponse, TokenPair } from "@/shared/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error(
    "VITE_API_BASE_URL is not defined. Check your .env file."
  );
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15_000, // 15s — generous for AI endpoints, strict for auth
});

// ---------------------------------------------------------------------------
// State accessors — lazy-imported to break circular dependency
// (axios.ts → auth-store.ts → axios.ts)
// ---------------------------------------------------------------------------

type AuthStoreAccessor = {
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  setTokens: (tokens: TokenPair) => void;
  logout: () => void;
};

let authAccessor: AuthStoreAccessor | null = null;

/**
 * Called once from auth-store.ts after the store is created.
 * This breaks the circular dependency: axios doesn't import the store
 * at module load time — the store registers itself after creation.
 */
export function registerAuthAccessor(accessor: AuthStoreAccessor): void {
  authAccessor = accessor;
}

// ---------------------------------------------------------------------------
// Request interceptor — attach Bearer token
// ---------------------------------------------------------------------------

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authAccessor?.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response interceptor — silent 401 refresh
// ---------------------------------------------------------------------------

// Tracks whether a refresh is already in-flight to avoid duplicate refreshes
// when multiple requests fail simultaneously.
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null): void {
  failedQueue.forEach(({ resolve, reject }) => {
    if (token) {
      resolve(token);
    } else {
      reject(error);
    }
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401, and not on the refresh endpoint itself
    // (to prevent infinite loops), and only if we have the auth accessor
    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest.url === "/auth/refresh" ||
      !authAccessor
    ) {
      return Promise.reject(error);
    }

    // If a refresh is already in-flight, queue this request
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((newToken) => {
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return api(originalRequest);
      });
    }

    isRefreshing = true;
    const refreshToken = authAccessor.getRefreshToken();

    if (!refreshToken) {
      authAccessor.logout();
      isRefreshing = false;
      return Promise.reject(error);
    }

    try {
      // Call refresh endpoint directly (not through this interceptor)
      const { data } = await axios.post<TokenPair>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken },
        { headers: { "Content-Type": "application/json" } }
      );

      authAccessor.setTokens(data);
      processQueue(null, data.access_token);

      // Retry the original request with the new token
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      }
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      authAccessor.logout();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
