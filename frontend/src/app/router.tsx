/**
 * Application router — all route definitions in one place.
 *
 * Wires the AppLayout shell, ProtectedRoute guard, and DashboardOverview.
 */

import { Routes, Route, Navigate, Link } from "react-router-dom";
import { Sparkles, ArrowRight, Zap, CheckCircle, BarChart3, Cpu, Layers } from "lucide-react";

import { LoginForm } from "@/features/auth/components/login-form";
import { RegisterForm } from "@/features/auth/components/register-form";
import { ProtectedRoute } from "@/features/auth/components/protected-route";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import { AppLayout } from "@/shared/components/layout/app-layout";
import { RoleDashboard } from "@/features/dashboard/components/role-dashboard";
import { JobList } from "@/features/jobs/components/job-list";
import { ResumeCenterPage } from "@/features/resume-center/components/resume-center-page";
import { CandidateScreeningPage } from "@/features/candidates/components/candidate-screening-page";
import { AnalyticsPage } from "@/features/analytics/components/analytics-page";
import { SettingsPage } from "@/features/settings/components/settings-page";
import { CareerGrowthPage } from "@/features/career-growth/components/career-growth-page";
import { CodingPracticePage } from "@/features/coding-practice/components/coding-practice-page";
import { CareerCoachPage } from "@/features/career-coach/components/career-coach-page";
import { NotificationCenterPage } from "@/features/notifications/components/notification-center-page";
import { LegalPage } from "@/features/legal/components/legal-page";

// ---------------------------------------------------------------------------
// Page layouts & Placeholders for future feature steps
// ---------------------------------------------------------------------------

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="relative z-10 w-full max-w-md">
        {children}
      </div>
    </div>
  );
}



// ---------------------------------------------------------------------------
// Home Landing Page
// ---------------------------------------------------------------------------

function HomePage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="relative min-h-screen flex flex-col justify-between bg-background">
      {/* Top Navbar */}
      <header className="relative z-10 flex items-center justify-between px-6 sm:px-12 py-5 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="flex items-center gap-2.5">
          <div className="flex size-10 items-center justify-center rounded-xl bg-fuchsia-600 text-white shadow-md">
            <Sparkles className="size-5" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">
            Hire<span className="text-fuchsia-400">Sense</span> <span className="text-[10px] px-2 py-0.5 rounded-full bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 font-semibold uppercase tracking-wider">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="text-sm font-medium text-muted-foreground hover:text-fuchsia-400 transition-colors px-3 py-2"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="text-sm font-semibold text-white bg-fuchsia-600 hover:bg-fuchsia-700 rounded-xl px-5 py-2.5 transition-all shadow-md"
          >
            Create Account
          </Link>
        </div>
      </header>

      {/* Main Hero Section */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-4 py-16 max-w-6xl mx-auto space-y-12">
        {/* Feature Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card border-2 border-fuchsia-500/40 shadow-md text-xs font-extrabold text-foreground">
          <Zap className="size-4 text-fuchsia-400 fill-fuchsia-400" />
          <span className="text-foreground tracking-wide font-extrabold">
            Next-Generation Resume Intelligence & Candidate Evaluation
          </span>
        </div>

        {/* Hero Headline */}
        <div className="space-y-4 max-w-3xl">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight text-foreground">
            Evaluate Candidates <br />
            <span className="text-fuchsia-400">With AI Precision</span>
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Rank applicants objectively, analyze technical skill matrices, and extract explainable ATS compatibility scores using Gemini AI reasoning.
          </p>
        </div>

        {/* CTA Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-4 pt-2">
          <Link
            to="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 px-8 py-3.5 text-base font-semibold text-white shadow-lg transition-all"
          >
            <span>Start Candidate Evaluation</span>
            <ArrowRight className="size-5" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-8 py-3.5 text-base font-medium text-foreground hover:bg-accent transition-all"
          >
            <span>Sign In to Portal</span>
          </Link>
        </div>

        {/* Feature Showcase Cards Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 text-left w-full">
          {/* Card 1: ATS Resume Matcher */}
          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4 relative overflow-hidden group">
            <div className="size-11 rounded-xl bg-fuchsia-500/10 text-fuchsia-400 flex items-center justify-center border border-fuchsia-500/20">
              <BarChart3 className="size-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-foreground group-hover:text-fuchsia-300 transition-colors">
                ATS Compatibility Scoring
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Vector embedding semantic matching algorithm compares candidate resumes directly against Job Specifications.
              </p>
            </div>
            {/* Visual Indicator Pill */}
            <div className="p-3 rounded-xl bg-background/80 border border-border/40 space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-muted-foreground">Match Score</span>
                <span className="text-emerald-400">94.8% Match</span>
              </div>
              <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[94.8%]" />
              </div>
            </div>
          </div>

          {/* Card 2: AI Skill Breakdown */}
          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4 relative overflow-hidden group">
            <div className="size-11 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
              <Cpu className="size-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-foreground group-hover:text-purple-300 transition-colors">
                Gemini Reasoning Analysis
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                NLP extraction identifies verified tech stacks, candidate strengths, potential red flags, and interview focus points.
              </p>
            </div>
            {/* Visual Skill Matrix Pills */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[11px] px-2.5 py-1 rounded-md bg-fuchsia-500/15 text-fuchsia-300 font-medium">FastAPI</span>
              <span className="text-[11px] px-2.5 py-1 rounded-md bg-purple-500/15 text-purple-300 font-medium">React + TS</span>
              <span className="text-[11px] px-2.5 py-1 rounded-md bg-pink-500/15 text-pink-300 font-medium">PyMuPDF</span>
              <span className="text-[11px] px-2.5 py-1 rounded-md bg-emerald-500/15 text-emerald-300 font-medium">MongoDB</span>
            </div>
          </div>

          {/* Card 3: Recruiter Workflow */}
          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4 relative overflow-hidden group">
            <div className="size-11 rounded-xl bg-pink-500/10 text-pink-400 flex items-center justify-center border border-pink-500/20">
              <Layers className="size-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-foreground group-hover:text-pink-300 transition-colors">
                Streamlined Pipeline
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Bulk PDF resume processing, role-based recruiter access, and automated candidate ranking reports.
              </p>
            </div>
            {/* Visual Checklist */}
            <div className="space-y-1.5 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle className="size-3.5 text-fuchsia-400" />
                <span>Instant PDF Parsing & Formatting</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="size-3.5 text-fuchsia-400" />
                <span>Explainable Criteria Evaluations</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 py-6 text-center text-xs text-muted-foreground bg-background/80 backdrop-blur-md">
        NipunHire AI &copy; 2026. Production-Grade Candidate Evaluation Architecture.
      </footer>
    </div>
  );
}

// ---------------------------------------------------------------------------
// App Router
// ---------------------------------------------------------------------------

export function AppRouter() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/terms" element={<LegalPage title="Terms of Service" />} />
      <Route path="/privacy-policy" element={<LegalPage title="Privacy Policy" />} />
      <Route path="/cookie-policy" element={<LegalPage title="Cookie Policy" />} />
      <Route
        path="/login"
        element={
          <AuthLayout>
            <LoginForm />
          </AuthLayout>
        }
      />
      <Route
        path="/register"
        element={
          <AuthLayout>
            <RegisterForm />
          </AuthLayout>
        }
      />

      {/* Protected routes wrapped in AppLayout shell */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<RoleDashboard />} />
          <Route path="/jobs" element={<JobList />} />
          <Route path="/resumes" element={<ResumeCenterPage />} />
          <Route path="/candidates" element={<CandidateScreeningPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/career-growth" element={<CareerGrowthPage />} />
          <Route path="/coding-practice" element={<CodingPracticePage />} />
          <Route path="/career-coach" element={<CareerCoachPage />} />
          <Route path="/notifications" element={<NotificationCenterPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
