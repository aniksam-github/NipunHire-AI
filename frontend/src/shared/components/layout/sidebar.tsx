/**
 * Sidebar — main navigation drawer for recruiter & candidate portals.
 */

import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Users,
  BarChart2,
  BrainCircuit,
  Code2,
  Bot,
  Target,
  Settings,
  Sparkles,
  LogOut,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { useAuthStore } from "@/features/auth/stores/auth-store";

interface SidebarProps {
  className?: string;
}

const recruiterNavItems = [
  { label: "Overview", path: "/dashboard", icon: LayoutDashboard },
  { label: "Job Positions", path: "/jobs", icon: Briefcase },
  { label: "Resume Screening", path: "/resumes", icon: FileText },
  { label: "Candidates", path: "/candidates", icon: Users },
  { label: "Analytics", path: "/analytics", icon: BarChart2 },
  { label: "Settings", path: "/settings", icon: Settings },
];

const candidateNavItems = [
  { label: "Overview", path: "/dashboard", icon: LayoutDashboard },
  { label: "Resume Center", path: "/resumes", icon: FileText },
  { label: "Job Matching", path: "/candidates", icon: Target },
  { label: "Applications", path: "/analytics", icon: BarChart2 },
  { label: "Career Growth", path: "/career-growth", icon: BrainCircuit },
  { label: "Coding Practice", path: "/coding-practice", icon: Code2 },
  { label: "AI Career Coach", path: "/career-coach", icon: Bot },
  { label: "Settings", path: "/settings", icon: Settings },
];

export function Sidebar({ className }: SidebarProps) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navItems = user?.role === "recruiter" || user?.role === "admin" ? recruiterNavItems : candidateNavItems;

  return (
    <aside
      className={cn(
        "flex flex-col justify-between w-64 bg-card border-r border-border p-4 h-screen sticky top-0 z-20 shadow-xl",
        className
      )}
    >
      {/* Brand Header */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="flex size-10 items-center justify-center rounded-xl bg-fuchsia-600 text-white shadow-md">
            <Sparkles className="size-5" />
          </div>
          <div>
            <div className="text-lg font-bold tracking-tight text-foreground flex items-center gap-1">
              Hire<span className="text-fuchsia-400">Sense</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-fuchsia-500/20 text-fuchsia-300 font-extrabold uppercase">
                AI
              </span>
            </div>
            <p className="text-[11px] font-semibold text-foreground/70">{user?.role === "recruiter" || user?.role === "admin" ? "Recruiter Suite" : "Candidate Suite"}</p>
          </div>
        </div>

        {/* Role Badge Pill */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-secondary/80 border border-border/60">
          <ShieldCheck className="size-4 text-fuchsia-400" />
          <div className="text-xs">
            <span className="text-foreground/70 font-medium">Portal: </span>
            <span className="font-bold text-foreground capitalize">{user?.role ?? "Candidate"}</span>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="space-y-1">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-foreground/60 mb-2">
            Main Menu
          </p>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all group",
                  isActive
                    ? "bg-fuchsia-600 text-white shadow-md"
                    : "text-foreground/80 hover:bg-accent hover:text-foreground"
                )
              }
            >
              <div className="flex items-center gap-3">
                <item.icon className="size-4" />
                <span>{item.label}</span>
              </div>
              <ChevronRight className="size-3.5 opacity-50 group-hover:opacity-100 transition-opacity" />
            </NavLink>
          ))}
        </nav>
      </div>

      {/* User Profile Footer */}
      <div className="pt-4 border-t border-border space-y-3">
        <div className="flex items-center gap-3 px-2">
          <div className="size-9 rounded-full bg-fuchsia-600/20 border border-fuchsia-500/30 text-fuchsia-400 flex items-center justify-center font-bold text-xs">
            {user?.full_name?.charAt(0) ?? "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-foreground truncate">{user?.full_name ?? "User Name"}</p>
            <p className="text-[11px] font-medium text-foreground/70 truncate">{user?.email ?? "user@domain.com"}</p>
          </div>
        </div>

        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-destructive/10 hover:bg-destructive/20 text-destructive text-xs font-bold transition-colors"
        >
          <LogOut className="size-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
