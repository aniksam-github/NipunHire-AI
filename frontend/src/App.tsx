/**
 * Root App component — composes providers + router.
 *
 * This is the single top-level component. All global concerns
 * (providers, router, error boundaries) are wired here.
 * Feature-specific code lives in features/ — this file stays thin.
 */

import { Providers } from "@/app/providers";
import { AppRouter } from "@/app/router";

export function App() {
  return (
    <Providers>
      <AppRouter />
    </Providers>
  );
}
