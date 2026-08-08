import { useAuthStore } from "@/features/auth/stores/auth-store";
import { DashboardOverview } from "./dashboard-overview";
import { RecruiterDashboardOverview } from "./recruiter-dashboard-overview";

export function RoleDashboard() {
  const role = useAuthStore((state) => state.user?.role);
  return role === "recruiter" || role === "admin" ? <RecruiterDashboardOverview /> : <DashboardOverview />;
}
