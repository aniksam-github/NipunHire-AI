/**
 * Candidate Dashboard — personal career progress, guided onboarding stepper, and AI career recommendations.
 * Implements Golden Rule #1 (Guide, don't overwhelm) & Checklist Items #7, #8, #11, #13 with user dismissal persistence.
 */

import { useState, useEffect } from "react";
import {
  BrainCircuit,
  Code2,
  FileText,
  Sparkles,
  Target,
  Upload,
  ChevronRight,
  CheckCircle2,
  Bot,
  Zap,
  X,
  RotateCcw,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { ScoreCard, SkillTag, HumanDecisionTrustBadge } from "@/shared/design-system";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import { useCandidateDashboard } from "../hooks/use-dashboard";

export function DashboardOverview() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const { data: dashboard } = useCandidateDashboard();

  const stepperStorageKey = `nipunhire_candidate_stepper_dismissed_${user?.id ?? "guest"}`;
  const [isStepperDismissed, setIsStepperDismissed] = useState(() => {
    return localStorage.getItem(stepperStorageKey) === "true";
  });

  const handleDismissStepper = () => {
    localStorage.setItem(stepperStorageKey, "true");
    setIsStepperDismissed(true);
  };

  const handleRestoreStepper = () => {
    localStorage.removeItem(stepperStorageKey);
    setIsStepperDismissed(false);
  };

  const applications = dashboard
    ? Object.values(dashboard.application_summary).reduce((total, count) => total + count, 0)
    : "—";

  const recommendations = dashboard?.daily_recommendations ?? [
    "Upload your PDF resume to receive an explainable ATS compatibility health score.",
    "Practice an adaptive multi-turn AI interview tailored to your primary tech stack.",
  ];

  const skillSuggestions = dashboard?.skill_improvement_suggestions ?? [
    "Run a job match evaluation to identify missing skill focus points.",
  ];

  const journeySteps = [
    {
      step: 1,
      title: "Evaluate Resume",
      desc: "ATS Health Check",
      icon: Upload,
      path: "/resumes",
      completed: (dashboard?.resume_health_score ?? 0) > 0,
    },
    {
      step: 2,
      title: "Job Matching",
      desc: "Factor Match Breakdown",
      icon: Target,
      path: "/candidates",
      completed: false,
    },
    {
      step: 3,
      title: "AI Interview",
      desc: "Adaptive Mock Sessions",
      icon: Bot,
      path: "/interviews",
      completed: (dashboard?.upcoming_interviews ?? 0) > 0,
    },
    {
      step: 4,
      title: "Career Growth",
      desc: "AI Blueprint & Coaching",
      icon: BrainCircuit,
      path: "/career-growth",
      completed: false,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Welcome back, {user?.full_name ?? "Candidate"}!</span>
            <Sparkles className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Your personal career acceleration workspace is ready.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {isStepperDismissed && (
            <Button
              onClick={handleRestoreStepper}
              variant="outline"
              className="h-10 rounded-xl border-border text-xs font-bold gap-1.5"
              title="Show onboarding stepper"
            >
              <RotateCcw className="size-3.5 text-fuchsia-400" />
              <span>Show Onboarding Guide</span>
            </Button>
          )}
          <Button
            onClick={() => navigate("/interviews")}
            className="h-10 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2"
          >
            <Bot className="size-4" /> Start AI Interview
          </Button>
          <Button
            onClick={() => navigate("/resumes")}
            variant="outline"
            className="h-10 rounded-xl border-border text-foreground font-bold text-xs gap-2"
          >
            <Upload className="size-4 text-fuchsia-400" /> Evaluate Resume
          </Button>
        </div>
      </div>

      {/* Guided 4-Step Journey Stepper with Remembered User Dismissal (Checklist Item #13 & Point #4) */}
      {!isStepperDismissed && (
        <section className="glass-card p-6 rounded-2xl border border-fuchsia-500/30 bg-gradient-to-r from-fuchsia-950/20 via-background to-purple-950/20 shadow-xl space-y-4 animate-fade-in relative">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-wider text-fuchsia-400">
                <Zap className="size-3.5 fill-fuchsia-400" />
                <span>Recommended Guided Career Journey</span>
              </div>
              <h3 className="text-base font-extrabold text-foreground">
                Follow your 4-step path to interview readiness
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-muted-foreground hidden sm:inline">
                Step-by-step guidance
              </span>
              <button
                onClick={handleDismissStepper}
                className="p-1 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors text-xs font-bold flex items-center gap-1"
                title="Dismiss onboarding guide"
              >
                <X className="size-4" />
                <span className="text-[11px] hidden sm:inline">Dismiss</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
            {journeySteps.map((s) => {
              const Icon = s.icon;
              return (
                <button
                  key={s.step}
                  onClick={() => navigate(s.path)}
                  className="flex items-start gap-3 p-3.5 rounded-xl bg-background/80 hover:bg-fuchsia-500/10 border border-border hover:border-fuchsia-500/40 text-left transition-all group"
                >
                  <div className="size-9 rounded-lg bg-fuchsia-500/15 text-fuchsia-400 border border-fuchsia-500/30 flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                    {s.completed ? <CheckCircle2 className="size-4 text-emerald-400" /> : <Icon className="size-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">
                      Step 0{s.step}
                    </div>
                    <div className="text-xs font-bold text-foreground truncate group-hover:text-fuchsia-300 transition-colors">
                      {s.title}
                    </div>
                    <div className="text-[11px] font-semibold text-foreground/70 truncate">
                      {s.desc}
                    </div>
                  </div>
                  <ChevronRight className="size-4 text-muted-foreground/50 group-hover:text-fuchsia-400 transition-colors shrink-0 mt-2" />
                </button>
              );
            })}
          </div>
        </section>
      )}

      {/* Top Actionable Score Metrics (Checklist Item #8 - Restraint) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard
          title="Profile Completion"
          value={dashboard ? `${dashboard.profile_completion_percentage}%` : "—"}
          description="Career profile readiness"
          icon={<FileText className="size-5" />}
          trend="Keep your profile current"
        />
        <ScoreCard
          title="Resume Health Score"
          value={dashboard?.resume_health_score ? `${dashboard.resume_health_score}%` : "—"}
          description="Primary resume ATS score"
          icon={<FileText className="size-5" />}
          trend="Improve with AI feedback"
        />
        <ScoreCard
          title="Applications Tracked"
          value={applications}
          description="Career opportunities in progress"
          icon={<Target className="size-5" />}
          trend="Stay on top of applications"
        />
        <ScoreCard
          title="Upcoming Interviews"
          value={dashboard?.upcoming_interviews ?? "—"}
          description="Scheduled practice sessions"
          icon={<BrainCircuit className="size-5" />}
          trend="Prepare with AI sessions"
        />
      </div>

      {/* Mandatory Decision-Support Trust Badge (Checklist Item #11) */}
      <HumanDecisionTrustBadge message="All AI recommendations, resume health indices, and skill breakdown scores are explainable decision-support signals designed to assist your career growth." />

      {/* AI Recommendations & Quick Self-Evaluation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 glass-card p-6 rounded-2xl border border-border space-y-5">
          <div>
            <h3 className="text-lg font-extrabold text-foreground">
              Your AI Career Recommendations
            </h3>
            <p className="text-xs font-semibold text-foreground/80">
              Personalized actions based on your profile and ATS evaluation.
            </p>
          </div>
          <div className="space-y-3">
            {recommendations.map((recommendation, i) => (
              <div
                key={i}
                className="p-4 rounded-xl bg-background border border-border/80 text-xs font-semibold text-foreground flex items-start gap-2.5"
              >
                <Sparkles className="size-4 text-fuchsia-400 shrink-0 mt-0.5" />
                <span>{recommendation}</span>
              </div>
            ))}
          </div>
          <div className="pt-2">
            <h4 className="text-xs font-extrabold mb-2 uppercase tracking-wider text-muted-foreground">
              Suggested Skill Improvement Focus
            </h4>
            <div className="flex flex-wrap gap-2">
              {skillSuggestions.map((suggestion, i) => (
                <SkillTag key={i} name={suggestion} status="neutral" />
              ))}
            </div>
          </div>
        </section>

        <section className="glass-card p-6 rounded-2xl border border-border space-y-5">
          <div>
            <h3 className="text-base font-extrabold text-foreground">Quick Action Hub</h3>
            <p className="text-xs text-foreground/70 mt-1">
              Select an action to continue your preparation.
            </p>
          </div>
          <div className="space-y-3">
            <Button
              onClick={() => navigate("/resumes")}
              variant="outline"
              className="w-full justify-start gap-2.5 font-bold text-xs"
            >
              <Upload className="size-4 text-fuchsia-400" />
              <span>Analyze & Edit Resume</span>
            </Button>
            <Button
              onClick={() => navigate("/interviews")}
              variant="outline"
              className="w-full justify-start gap-2.5 font-bold text-xs"
            >
              <Bot className="size-4 text-fuchsia-400" />
              <span>Practice AI Mock Interview</span>
            </Button>
            <Button
              onClick={() => navigate("/coding-practice")}
              variant="outline"
              className="w-full justify-start gap-2.5 font-bold text-xs"
            >
              <Code2 className="size-4 text-fuchsia-400" />
              <span>Practice Technical Coding</span>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
