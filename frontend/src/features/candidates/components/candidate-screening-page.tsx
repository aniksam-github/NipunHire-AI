/**
 * CandidateScreeningPage — main view for candidate rankings & AI match evaluations.
 */

import { useState } from "react";
import { Users, Sparkles, Plus, CheckCircle2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { CandidateMatchCard } from "./candidate-match-card";
import { CandidateMatchModal } from "./candidate-match-modal";
import type { MatchResponse } from "../types";
import { useJobsList } from "@/features/jobs/hooks/use-jobs";

export function CandidateScreeningPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeEvaluations, setActiveEvaluations] = useState<MatchResponse[]>([]);
  const { data: jobs = [] } = useJobsList();

  const handleMatchSuccess = (result: MatchResponse) => {
    setActiveEvaluations((prev) => [result, ...prev.filter((item) => item.id !== result.id)]);
  };

  const getJobTitle = (jobId: string) => {
    return jobs.find((j) => j.id === jobId)?.title ?? "Selected Position";
  };

  return (
    <div className="space-y-6">
      {/* Top Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Candidate Evaluation & Screening</span>
            <Users className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Compare candidate tech skill matrices against job requirements with Gemini AI reasoning.
          </p>
        </div>

        <Button
          onClick={() => setIsModalOpen(true)}
          className="h-11 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2"
        >
          <Plus className="size-4" />
          <span>Run AI Match Screening</span>
        </Button>
      </div>

      {/* Main Content Area */}
      {activeEvaluations.length === 0 ? (
        <div className="glass-card p-12 rounded-2xl border border-border text-center space-y-4 max-w-md mx-auto">
          <div className="size-14 rounded-2xl bg-fuchsia-600/15 text-fuchsia-400 flex items-center justify-center mx-auto border border-fuchsia-500/20 shadow-md">
            <Sparkles className="size-7" />
          </div>
          <h3 className="text-xl font-extrabold text-foreground">No Evaluation Active</h3>
          <p className="text-xs font-semibold text-foreground/80">
            Select a target Job Position and Candidate Resume to run live Gemini AI match scoring and skill gap analysis.
          </p>
          <Button
            onClick={() => setIsModalOpen(true)}
            className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs gap-2"
          >
            <Sparkles className="size-4" />
            <span>Evaluate Match Now</span>
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold uppercase tracking-wider text-foreground/80 flex items-center gap-1.5">
              <CheckCircle2 className="size-4 text-emerald-400" />
              <span>Active AI Evaluation Scorecards ({activeEvaluations.length})</span>
            </span>
          </div>

          <div className="space-y-6">
            {activeEvaluations.map((evalResult) => (
              <CandidateMatchCard
                key={evalResult.id}
                match={evalResult}
                jobTitle={getJobTitle(evalResult.job_id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Candidate Match Modal */}
      <CandidateMatchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onMatchSuccess={handleMatchSuccess}
      />
    </div>
  );
}
