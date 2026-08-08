/**
 * TanStack Query client — centralized configuration.
 *
 * All React Query hooks across the app share this single client instance.
 * Sensible defaults:
 *   - staleTime: 5 min — avoids refetching data the user just saw
 *   - retry: 1 — one retry on transient failures, not three (the default)
 *   - refetchOnWindowFocus: false — prevents jarring re-fetches when
 *     the user tabs back; we refetch explicitly when needed
 */

import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0, // Don't retry mutations — they're not idempotent
    },
  },
});
