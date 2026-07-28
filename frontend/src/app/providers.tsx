/**
 * App-level providers — wraps the entire application.
 *
 * All global providers (React Query, future theme provider, etc.)
 * are composed here in a single component so main.tsx stays clean.
 * Adding a new provider means adding it here, not hunting through
 * nested JSX in the entry point.
 */

import type { ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "@/shared/components/ui/sonner";
import { queryClient } from "@/shared/lib/query-client";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
