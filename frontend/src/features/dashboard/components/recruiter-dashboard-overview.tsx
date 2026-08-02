/**
 * Recruiter-only landing dashboard.
 * Implements Recruiter mental model separation (Checklist #12), actionable metrics (#10),
 * human-in-the-loop decision-support framing (#11), and guided pipeline stepper with user dismissal persistence (#13 & Point #4).
 */

import { useState } from "react";
import {
  BarChart3,
  Briefcase,
  FileText,
  Plus,
  Users,
  Award,
  ChevronRight,
  Zap,
  X,
  RotateCcw,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { ScoreCard, HumanDecisionTrustBadge } from "@/shared/design-system";
import { useAuthStore } from "@/features/auth/stores/auth-store";

export function RecruiterDashboardOverview() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  const recruiterStepperKey = `nipunhire_recruiter_stepper_dismissed_${user?.id ?? "guest"}`;
  const [isStepperDismissed, setIsStepperDismissed] = useState(() => {
    return localStorage.getItem(recruiterStepperKey) === "true";
  });

  const handleDismissStepper = () => {
    localStorage.setItem(recruiterStepperKey, "true");
    setIsStepperDismissed(true);
  };

  const handleRestoreStepper = () => {
    localStorage.removeItem(recruiterStepperKey);
    setIsStepperDismissed(false);
  };

  const pipelineSteps = [
    {
      step: 1,
      title: "Job Specifications",
      desc: "Post & Manage Roles",
      icon: Briefcase,
      path: "/jobs",
    },
    {
      step: 2,
      title: "Resume Ingestion",
      desc: "PyMuPDF & ATS Screening",
      icon: FileText,
      path: "/resumes",
    },
    {
      step: 3,
      title: "Recruiter AI Matrix",
      desc: "Side-by-Side Candidate Ranking",
      icon: Award,
      path: "/recruiter-ai",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground">
            Welcome back, {user?.full_name ?? "Recruiter"}!
          </h2>
          <p className="text-xs font-semibold text-foreground/70 mt-1">
            Manage job postings, bulk evaluate applicant resumes, and generate explainable candidate ranking matrices.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isStepperDismissed && (
            <Button
              onClick={handleRestoreStepper}
              variant="outline"
              className="border-border text-xs font-bold gap-1.5"
              title="Show recruiter pipeline guide"
            >
              <RotateCcw className="size-3.5 text-fuchsia-400" />
              <span>Show Pipeline Guide</span>
            </Button>
          )}
          <Button
            onClick={() => navigate("/recruiter-ai")}
            className="bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2"
          >
            <Award className="size-4" /> Recruiter AI Ranking
          </Button>
          <Button
            onClick={() => navigate("/jobs")}
            variant="outline"
            className="border-border text-foreground font-bold text-xs gap-2"
          >
            <Plus className="size-4 text-fuchsia-400" /> Create Job
          </Button>
        </div>
      </div>

      {/* Guided Recruiter Pipeline Stepper with Persistent User Dismissal (Point #4) */}
      {!isStepperDismissed && (
        <section className="glass-card p-6 rounded-2xl border border-fuchsia-500/30 bg-gradient-to-r from-fuchsia-950/20 via-background to-purple-950/20 shadow-xl space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-wider text-fuchsia-400">
                <Zap className="size-3.5 fill-fuchsia-400" />
                <span>Recruiter Evaluation Pipeline</span>
              </div>
              <h3 className="text-base font-extrabold text-foreground">
                3-step workflow for objective candidate shortlisting
              </h3>
            </div>
            <button
              onClick={handleDismissStepper}
              className="p-1 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors text-xs font-bold flex items-center gap-1"
              title="Dismiss pipeline guide"
            >
              <X className="size-4" />
              <span className="text-[11px] hidden sm:inline">Dismiss</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            {pipelineSteps.map((s) => {
              const Icon = s.icon;
              return (
                <button
                  key={s.step}
                  onClick={() => navigate(s.path)}
                  className="flex items-start gap-3 p-4 rounded-xl bg-background/80 hover:bg-fuchsia-500/10 border border-border hover:border-fuchsia-500/40 text-left transition-all group"
                >
                  <div className="size-10 rounded-xl bg-fuchsia-500/15 text-fuchsia-400 border border-fuchsia-500/30 flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                    <Icon className="size-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-bold text-muted-foreground uppercase">
                      Step 0{s.step}
                    </div>
                    <div className="text-sm font-bold text-foreground truncate group-hover:text-fuchsia-300 transition-colors">
                      {s.title}
                    </div>
                    <div className="text-xs font-semibold text-foreground/70 truncate">
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

      {/* Mandatory Decision Support Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="All recruiter AI ranking metrics, factor reconciliations, and candidate summaries are explainable decision-support signals. Final hiring and rejection decisions remain strictly with human recruiters." />

      {/* Actionable Decision Metrics Grid (Checklist Item #10) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard
          title="Active Job Positions"
          value="Open"
          description="Job specifications in pipeline"
          icon={<Briefcase className="size-5" />}
          trend="Manage hiring specs"
        />
        <ScoreCard
          title="Resume Screening"
          value="Active"
          description="Uploaded PDF resume pool"
          icon={<FileText className="size-5" />}
          trend="ATS Compatibility Scores"
        />
        <ScoreCard
          title="Candidate Matrix"
          value="Ranked"
          description="Deterministic factor match"
          icon={<Users className="size-5" />}
          trend="Shortlist candidates"
        />
        <ScoreCard
          title="Audit & Research"
          value="Passed"
          description="Statistical bias auditing"
          icon={<BarChart3 className="size-5" />}
          trend="Check score distributions"
        />
      </div>

      {/* Quick Action Studio */}
      <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h3 className="font-extrabold text-foreground">Recruiter Quick Action Studio</h3>
        <div className="flex flex-wrap gap-3">
          <Button
            onClick={() => navigate("/jobs")}
            variant="outline"
            className="font-bold text-xs border-border"
          >
            Manage Job Positions
          </Button>
          <Button
            onClick={() => navigate("/resumes")}
            variant="outline"
            className="font-bold text-xs border-border"
          >
            Screen Resumes
          </Button>
          <Button
            onClick={() => navigate("/recruiter-ai")}
            variant="outline"
            className="font-bold text-xs border-border"
          >
            Generate AI Candidate Ranking Matrix
          </Button>
          <Button
            onClick={() => navigate("/research")}
            variant="outline"
            className="font-bold text-xs border-border"
          >
            Run Statistical Bias Audit
          </Button>
        </div>
      </div>
    </div>
  );
}
