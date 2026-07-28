/**
 * ProtectedRoute — route guard that redirects unauthenticated users.
 *
 * Wraps any route that requires authentication. If the user has no
 * access token in the store, they're redirected to /login immediately.
 *
 * This is a thin wrapper — it checks Zustand state, not the API.
 * The actual token validation happens when the protected page's
 * queries fire (via Axios interceptors + useCurrentUser).
 *
 * Why not call /auth/me here?
 *   - It would add latency to every route transition
 *   - The Axios interceptor already handles expired tokens silently
 *   - useCurrentUser runs inside the dashboard layout, not the guard
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "../stores/auth-store";

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    // Preserve the intended destination so we can redirect back after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Render the child route
  return <Outlet />;
}
