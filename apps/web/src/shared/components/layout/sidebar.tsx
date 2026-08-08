/**
 * Sidebar — persona-divergent navigation drawer for Recruiter & Candidate hubs (Checklist #12).
 * Groups 15+ features into 4-5 intuitive logical hubs instead of flat navigation.
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
  Award,
  Layers,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { useAuthStore } from "@/features/auth/stores/auth-store";

interface SidebarProps {
  className?: string;
}

interface NavSection {
  title: string;
  items: {
    label: string;
    path: string;
    icon: React.ElementType;
    badge?: string;
  }[];
}

const recruiterSections: NavSection[] = [
  {
    title: "Overview",
    items: [{ label: "Dashboard Overview", path: "/dashboard", icon: LayoutDashboard }],
  },
  {
    title: "Hiring & Screening Studio",
    items: [
      { label: "Job Positions", path: "/jobs", icon: Briefcase },
      { label: "Resume Screening", path: "/resumes", icon: FileText },
      { label: "Candidate Pool", path: "/candidates", icon: Users },
    ],
  },
  {
    title: "AI Candidate Intelligence",
    items: [
      { label: "Recruiter AI Ranking", path: "/recruiter-ai", icon: Award, badge: "AI" },
      { label: "Analytics & Pipeline", path: "/analytics", icon: BarChart2 },
    ],
  },
  {
    title: "Ethics & Compliance",
    items: [
      { label: "Research & Bias Audit", path: "/research", icon: BrainCircuit, badge: "Audit" },
      { label: "Settings", path: "/settings", icon: Settings },
    ],
  },
];

const candidateSections: NavSection[] = [
  {
    title: "Overview",
    items: [{ label: "Dashboard Overview", path: "/dashboard", icon: LayoutDashboard }],
  },
  {
    title: "Resume & ATS Studio",
    items: [
      { label: "Resume Center", path: "/resumes", icon: FileText },
      { label: "Job Match & ATS", path: "/candidates", icon: Target },
    ],
  },
  {
    title: "AI Practice Hub",
    items: [
      { label: "Adaptive AI Interview", path: "/interviews", icon: Bot, badge: "Live AI" },
      { label: "Coding Practice", path: "/coding-practice", icon: Code2 },
    ],
  },
  {
    title: "Career Acceleration",
    items: [
      { label: "AI Career Coach", path: "/career-coach", icon: Sparkles },
      { label: "Career Growth Plan", path: "/career-growth", icon: BrainCircuit },
      { label: "Application Tracker", path: "/analytics", icon: BarChart2 },
      { label: "Settings", path: "/settings", icon: Settings },
    ],
  },
];

export function Sidebar({ className }: SidebarProps) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const isRecruiter = user?.role === "recruiter" || user?.role === "admin";
  const sections = isRecruiter ? recruiterSections : candidateSections;

  return (
    <aside
      className={cn(
        "flex flex-col justify-between w-64 bg-card border-r border-border p-4 h-screen sticky top-0 z-20 shadow-xl overflow-y-auto",
        className
      )}
    >
      <div className="space-y-5">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="flex size-10 items-center justify-center rounded-xl bg-fuchsia-600 text-white shadow-md shrink-0">
            <Sparkles className="size-5" />
          </div>
          <div>
            <div className="text-lg font-bold tracking-tight text-foreground flex items-center gap-1">
              Hire<span className="text-fuchsia-400">Sense</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-fuchsia-500/20 text-fuchsia-300 font-extrabold uppercase">
                AI
              </span>
            </div>
            <p className="text-[11px] font-semibold text-foreground/70">
              {isRecruiter ? "Recruiter Suite" : "Candidate Suite"}
            </p>
          </div>
        </div>

        {/* Persona Shield Indicator */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-secondary/80 border border-border/60">
          <ShieldCheck className="size-4 text-fuchsia-400 shrink-0" />
          <div className="text-xs truncate">
            <span className="text-foreground/70 font-medium">Portal: </span>
            <span className="font-bold text-foreground capitalize">
              {user?.role ?? "Candidate"}
            </span>
          </div>
        </div>

        {/* Navigation Sections */}
        <nav className="space-y-4">
          {sections.map((section, sectionIdx) => (
            <div key={sectionIdx} className="space-y-1">
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/80">
                {section.title}
              </p>
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold transition-all group",
                      isActive
                        ? "bg-fuchsia-600 text-white shadow-md"
                        : "text-foreground/80 hover:bg-accent hover:text-foreground"
                    )
                  }
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <item.icon className="size-4 shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {item.badge && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-fuchsia-500/20 text-fuchsia-300 group-hover:bg-white/20 group-hover:text-white font-extrabold uppercase">
                        {item.badge}
                      </span>
                    )}
                    <ChevronRight className="size-3.5 opacity-40 group-hover:opacity-100 transition-opacity" />
                  </div>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
      </div>

      {/* User Profile Footer */}
      <div className="pt-4 mt-4 border-t border-border space-y-3">
        <div className="flex items-center gap-3 px-2">
          <div className="size-9 rounded-full bg-fuchsia-600/20 border border-fuchsia-500/30 text-fuchsia-400 flex items-center justify-center font-bold text-xs shrink-0">
            {user?.full_name?.charAt(0) ?? "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-foreground truncate">
              {user?.full_name ?? "User Name"}
            </p>
            <p className="text-[11px] font-medium text-foreground/70 truncate">
              {user?.email ?? "user@domain.com"}
            </p>
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
