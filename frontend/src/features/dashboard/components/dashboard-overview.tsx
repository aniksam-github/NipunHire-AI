/** Candidate dashboard: personal career progress and self-evaluation. */

import { BrainCircuit, Code2, FileText, Sparkles, Target, Upload } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { ScoreCard, SkillTag } from "@/shared/design-system";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import { useCandidateDashboard } from "../hooks/use-dashboard";

export function DashboardOverview() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const { data: dashboard } = useCandidateDashboard();
  const applications = dashboard
    ? Object.values(dashboard.application_summary).reduce((total, count) => total + count, 0)
    : "—";
  const recommendations = dashboard?.daily_recommendations ?? [
    "Upload a resume to receive an ATS health score and personalized recommendations.",
  ];
  const skillSuggestions = dashboard?.skill_improvement_suggestions ?? [
    "Run a job match after uploading your resume to identify a skill focus.",
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Welcome back, {user?.full_name ?? "Candidate"}!</span>
            <Sparkles className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">Your personal career workspace is ready for your next improvement.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={() => navigate("/career-growth")} className="h-10 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2">
            <BrainCircuit className="size-4" />Practice Interview
          </Button>
          <Button onClick={() => navigate("/resumes")} variant="outline" className="h-10 rounded-xl border-border text-foreground font-bold text-xs gap-2">
            <Upload className="size-4 text-fuchsia-400" />Evaluate Resume
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard title="Profile Completion" value={dashboard ? `${dashboard.profile_completion_percentage}%` : "—"} description="Career profile readiness" icon={<FileText className="size-5" />} trend="Keep your profile current" />
        <ScoreCard title="Resume Health Score" value={dashboard?.resume_health_score ? `${dashboard.resume_health_score}%` : "—"} description="Primary resume ATS score" icon={<FileText className="size-5" />} trend="Improve with AI feedback" />
        <ScoreCard title="Applications Tracked" value={applications} description="Career opportunities in progress" icon={<Target className="size-5" />} trend="Stay on top of every application" />
        <ScoreCard title="Upcoming Interviews" value={dashboard?.upcoming_interviews ?? "—"} description="Scheduled practice or real interviews" icon={<BrainCircuit className="size-5" />} trend="Prepare with mock sessions" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 glass-card p-6 rounded-2xl border border-border space-y-5">
          <div><h3 className="text-lg font-extrabold text-foreground">Your AI Career Recommendations</h3><p className="text-xs font-semibold text-foreground/80">Actions based on your profile, resume, and application data.</p></div>
          <div className="space-y-3">{recommendations.map((recommendation) => <div key={recommendation} className="p-4 rounded-xl bg-background border border-border/80 text-sm font-semibold text-foreground"><Sparkles className="inline size-4 mr-2 text-fuchsia-400" />{recommendation}</div>)}</div>
          <div className="pt-2"><h4 className="text-sm font-extrabold mb-2">Skill improvement focus</h4><div className="flex flex-wrap gap-2">{skillSuggestions.map((suggestion) => <SkillTag key={suggestion} name={suggestion} status="neutral" />)}</div></div>
        </section>

        <section className="glass-card p-6 rounded-2xl border border-border space-y-5">
          <div><h3 className="text-base font-extrabold text-foreground">Quick self-evaluation</h3><p className="text-xs text-foreground/70 mt-1">Build confidence one action at a time.</p></div>
          <div className="space-y-3">
            <Button onClick={() => navigate("/resumes")} variant="outline" className="w-full justify-start"><Upload />Analyze my resume</Button>
            <Button onClick={() => navigate("/career-growth")} variant="outline" className="w-full justify-start"><BrainCircuit />Practice interview</Button>
            <Button onClick={() => navigate("/coding-practice")} variant="outline" className="w-full justify-start"><Code2 />Practice coding</Button>
          </div>
        </section>
      </div>
    </div>
  );
}
