/** Recruiter-only landing dashboard. Candidate progress is intentionally kept separate. */

import { BarChart3, Briefcase, FileText, Plus, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { ScoreCard } from "@/shared/design-system";
import { useAuthStore } from "@/features/auth/stores/auth-store";

export function RecruiterDashboardOverview() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  return <div className="space-y-8">
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
      <div><h2 className="text-2xl font-extrabold">Welcome back, {user?.full_name ?? "Recruiter"}!</h2><p className="text-xs font-semibold text-foreground/70 mt-1">Manage open positions, evaluate resumes, and move candidates through your hiring pipeline.</p></div>
      <Button onClick={() => navigate("/jobs")} className="bg-fuchsia-600 hover:bg-fuchsia-700 text-white gap-2"><Plus className="size-4" />Create Job</Button>
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <ScoreCard title="Job Management" value="Open" description="Create and maintain job postings" icon={<Briefcase className="size-5" />} trend="Manage your hiring pipeline" />
      <ScoreCard title="Resume Screening" value="AI" description="Parse and evaluate uploaded resumes" icon={<FileText className="size-5" />} trend="Use ATS scores and skills" />
      <ScoreCard title="Candidate Matching" value="Ready" description="Compare candidates to job requirements" icon={<Users className="size-5" />} trend="Shortlist the best fit" />
      <ScoreCard title="Hiring Analytics" value="Live" description="Review application-stage metrics" icon={<BarChart3 className="size-5" />} trend="Track conversion and activity" />
    </div>
    <div className="glass-card p-6 rounded-2xl border border-border"><h3 className="font-extrabold">Recruiter quick actions</h3><div className="flex flex-wrap gap-3 mt-4"><Button onClick={() => navigate("/jobs")} variant="outline">Manage job postings</Button><Button onClick={() => navigate("/resumes")} variant="outline">Screen resumes</Button><Button onClick={() => navigate("/candidates")} variant="outline">Match candidates</Button></div></div>
  </div>;
}
