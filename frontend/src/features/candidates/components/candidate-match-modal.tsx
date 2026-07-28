/**
 * CandidateMatchModal — interactive modal to trigger live AI resume vs job matching evaluation.
 */

import { useState } from "react";
import { Loader2, Sparkles, X, Briefcase, FileText } from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import { Label } from "@/shared/components/ui/label";
import { useJobsList } from "@/features/jobs/hooks/use-jobs";
import { useResumesList } from "@/features/resume-center/hooks/use-resumes";
import { useCompareJobMatch } from "../hooks/use-candidates";
import type { MatchResponse } from "../types";

interface CandidateMatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onMatchSuccess: (result: MatchResponse) => void;
}

export function CandidateMatchModal({ isOpen, onClose, onMatchSuccess }: CandidateMatchModalProps) {
  const { data: jobs = [], isLoading: isLoadingJobs } = useJobsList();
  const { data: resumes = [], isLoading: isLoadingResumes } = useResumesList();

  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");

  const compareMutation = useCompareJobMatch();

  if (!isOpen) return null;

  const handleRunEvaluation = () => {
    const targetJobId = selectedJobId || (jobs[0]?.id ?? "");
    if (!targetJobId) {
      alert("Please select a job position to evaluate.");
      return;
    }

    compareMutation.mutate(
      {
        job_id: targetJobId,
        resume_id: selectedResumeId || undefined,
      },
      {
        onSuccess: (result) => {
          onMatchSuccess(result);
          onClose();
        },
      }
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md">
      <div className="w-full max-w-lg glass-card rounded-2xl border border-border shadow-2xl p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-fuchsia-600/20 text-fuchsia-400 border border-fuchsia-500/30">
              <Sparkles className="size-5" />
            </div>
            <div>
              <h3 className="text-xl font-extrabold text-foreground">Run AI Match Screening</h3>
              <p className="text-xs font-semibold text-foreground/80">Compare candidate resume against job requirements</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="size-8 rounded-lg text-muted-foreground hover:text-foreground">
            <X className="size-5" />
          </Button>
        </div>

        {/* Form Selection */}
        <div className="space-y-4">
          {/* Target Job Selection */}
          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
              <Briefcase className="size-3.5 text-fuchsia-400" />
              <span>Select Target Job Opening</span>
            </Label>
            {isLoadingJobs ? (
              <p className="text-xs text-foreground/70">Loading active jobs...</p>
            ) : jobs.length === 0 ? (
              <p className="text-xs text-destructive font-bold">No active job postings found. Post a job first!</p>
            ) : (
              <select
                value={selectedJobId || (jobs[0]?.id ?? "")}
                onChange={(e) => setSelectedJobId(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-background border border-border text-foreground text-sm font-medium focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 outline-none cursor-pointer"
              >
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} — {job.department} ({job.location})
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Target Resume Selection */}
          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
              <FileText className="size-3.5 text-fuchsia-400" />
              <span>Select Candidate Resume Version</span>
            </Label>
            {isLoadingResumes ? (
              <p className="text-xs text-foreground/70">Loading resumes...</p>
            ) : resumes.length === 0 ? (
              <p className="text-xs text-amber-400 font-bold">No candidate resume uploaded yet. Default evaluation will use system profile.</p>
            ) : (
              <select
                value={selectedResumeId}
                onChange={(e) => setSelectedResumeId(e.target.value)}
                className="w-full h-10 px-3 rounded-xl bg-background border border-border text-foreground text-sm font-medium focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 outline-none cursor-pointer"
              >
                <option value="">Use Primary / Latest Resume</option>
                {resumes.map((res) => (
                  <option key={res.id} value={res.id}>
                    {res.filename} (ATS: {res.ats_score}%)
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
          <Button type="button" variant="outline" onClick={onClose} className="rounded-xl border-border text-foreground font-bold">
            Cancel
          </Button>
          <Button
            onClick={handleHandleEvaluation}
            disabled={compareMutation.isPending || jobs.length === 0}
            className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold gap-2 shadow-md"
          >
            {compareMutation.isPending ? (
              <>
                <Loader2 className="animate-spin size-4" />
                <span>Running Gemini Reasoning...</span>
              </>
            ) : (
              <>
                <Sparkles className="size-4" />
                <span>Evaluate Match Score</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );

  function handleHandleEvaluation() {
    handleRunEvaluation();
  }
}
