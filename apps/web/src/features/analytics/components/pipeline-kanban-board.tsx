/**
 * PipelineKanbanBoard — interactive Kanban column view for candidate application tracking.
 */

import { useState } from "react";
import {
  FileText,
  ChevronRight,
  Clock,
  CheckCircle2,
  XCircle,
  Calendar,
  Award,
  Loader2,
} from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import type { ApplicationResponse, ApplicationStatus } from "../types";
import { useUpdateApplicationStatus } from "../hooks/use-analytics";
import { useJobsList } from "@/features/jobs/hooks/use-jobs";

interface PipelineKanbanBoardProps {
  applications: ApplicationResponse[];
}

const STAGES: { key: ApplicationStatus; label: string; color: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "applied", label: "Applied", color: "border-blue-500/40 text-blue-400 bg-blue-500/10", icon: FileText },
  { key: "shortlisted", label: "Shortlisted", color: "border-fuchsia-500/40 text-fuchsia-400 bg-fuchsia-500/10", icon: CheckCircle2 },
  { key: "interview_scheduled", label: "Interviewing", color: "border-purple-500/40 text-purple-400 bg-purple-500/10", icon: Calendar },
  { key: "offer_received", label: "Offered", color: "border-emerald-500/40 text-emerald-400 bg-emerald-500/10", icon: Award },
  { key: "rejected", label: "Rejected", color: "border-rose-500/40 text-rose-400 bg-rose-500/10", icon: XCircle },
];

export function PipelineKanbanBoard({ applications }: PipelineKanbanBoardProps) {
  const updateMutation = useUpdateApplicationStatus();
  const { data: jobs = [] } = useJobsList();
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);

  const getJobTitle = (jobId: string) => {
    return jobs.find((j) => j.id === jobId)?.title ?? `Job #${jobId.slice(-6)}`;
  };

  const handleAdvanceStatus = (app: ApplicationResponse) => {
    const nextStatusMap: Record<ApplicationStatus, ApplicationStatus> = {
      saved: "applied",
      applied: "shortlisted",
      shortlisted: "interview_scheduled",
      interview_scheduled: "offer_received",
      offer_received: "offer_received",
      rejected: "applied",
    };

    const nextStatus = nextStatusMap[app.status];
    if (nextStatus === app.status) return;

    setSelectedAppId(app.id);
    updateMutation.mutate(
      {
        id: app.id,
        payload: { status: nextStatus, note: `Advanced to ${nextStatus.replace("_", " ")}` },
      },
      {
        onSettled: () => setSelectedAppId(null),
      }
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-lg font-extrabold text-foreground">Candidate Application Pipeline</h3>
        <span className="text-xs font-semibold text-foreground/80">
          Click <span className="text-fuchsia-400 font-bold">Advance Stage</span> to progress candidate evaluation pipeline
        </span>
      </div>

      {/* Kanban Columns */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 overflow-x-auto pb-4">
        {STAGES.map((stage) => {
          const StageIcon = stage.icon;
          const stageApps = applications.filter((a) => a.status === stage.key);

          return (
            <div
              key={stage.key}
              className="glass-card p-4 rounded-2xl border border-border/80 space-y-3 min-w-[220px] bg-card/40 flex flex-col justify-between min-h-[360px]"
            >
              {/* Column Header */}
              <div className="space-y-2 border-b border-border/60 pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`p-1.5 rounded-lg border text-xs ${stage.color}`}>
                      <StageIcon className="size-4" />
                    </span>
                    <span className="text-sm font-bold text-foreground">{stage.label}</span>
                  </div>
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                    {stageApps.length}
                  </span>
                </div>
              </div>

              {/* Column Cards */}
              <div className="space-y-3 flex-1 overflow-y-auto max-h-[420px] pr-1">
                {stageApps.length === 0 ? (
                  <div className="p-4 rounded-xl border border-dashed border-border/60 text-center text-xs font-semibold text-foreground/70 my-4">
                    No candidates
                  </div>
                ) : (
                  stageApps.map((app) => {
                    const isUpdating = selectedAppId === app.id && updateMutation.isPending;

                    return (
                      <div
                        key={app.id}
                        className="p-3.5 rounded-xl bg-background border border-border/80 hover:border-fuchsia-500/50 transition-all space-y-2.5 shadow-xs group"
                      >
                        <div className="space-y-1">
                          <span className="text-[10px] font-mono text-fuchsia-400 uppercase font-bold">
                            App #{app.id.slice(-6)}
                          </span>
                          <h4 className="text-xs font-bold text-foreground group-hover:text-fuchsia-300 transition-colors line-clamp-1">
                            {getJobTitle(app.job_id)}
                          </h4>
                        </div>

                        <div className="flex items-center justify-between text-[10px] font-semibold text-foreground/70 pt-1 border-t border-border/40">
                          <span className="flex items-center gap-1">
                            <Clock className="size-3 text-fuchsia-400" />
                            {new Date(app.updated_at).toLocaleDateString()}
                          </span>

                          {app.status !== "offer_received" && app.status !== "rejected" && (
                            <Button
                              size="sm"
                              variant="ghost"
                              disabled={isUpdating}
                              onClick={() => handleAdvanceStatus(app)}
                              className="h-6 px-2 text-[10px] font-bold text-fuchsia-400 hover:text-fuchsia-300 hover:bg-fuchsia-500/10 gap-1 rounded-lg"
                            >
                              {isUpdating ? (
                                <Loader2 className="animate-spin size-3" />
                              ) : (
                                <>
                                  <span>Advance</span>
                                  <ChevronRight className="size-3" />
                                </>
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
