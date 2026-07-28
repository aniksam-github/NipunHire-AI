/**
 * AnalyticsPage — main page for recruiting analytics & candidate application pipeline.
 */

import { BarChart3, Loader2, Sparkles } from "lucide-react";
import { AnalyticsSummaryCards } from "./analytics-summary-cards";
import { PipelineKanbanBoard } from "./pipeline-kanban-board";
import { useApplicationsList } from "../hooks/use-analytics";

export function AnalyticsPage() {
  const { data: applications = [], isLoading } = useApplicationsList();

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Recruiting Analytics & Pipeline</span>
            <BarChart3 className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Track candidate pipeline stages, application conversion rates, and screening metrics.
          </p>
        </div>
      </div>

      {/* KPI Metric Summary Cards */}
      <AnalyticsSummaryCards applications={applications} />

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center p-12 space-y-3 glass-card rounded-2xl border border-border">
          <Loader2 className="animate-spin size-8 text-fuchsia-400" />
          <p className="text-xs font-bold text-foreground">Loading candidate application pipeline...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && applications.length === 0 && (
        <div className="glass-card p-12 rounded-2xl border border-border text-center space-y-4 max-w-md mx-auto">
          <div className="size-14 rounded-2xl bg-fuchsia-600/15 text-fuchsia-400 flex items-center justify-center mx-auto border border-fuchsia-500/20 shadow-md">
            <Sparkles className="size-7" />
          </div>
          <h3 className="text-xl font-extrabold text-foreground">No Applications Yet</h3>
          <p className="text-xs font-semibold text-foreground/80">
            Candidate job applications and pipeline tracking stages will appear here as applicants apply for open positions.
          </p>
        </div>
      )}

      {/* Kanban Pipeline Board */}
      {!isLoading && (
        <PipelineKanbanBoard applications={applications} />
      )}
    </div>
  );
}
