/**
 * StagedAIProgressIndicator — multi-step progress feedback during AI operations (Checklist #1).
 * Supports explicit staged error recovery states when AI calls time out or fail mid-operation (Checklist #2).
 */

import { useState, useEffect } from "react";
import { CheckCircle2, Loader2, Sparkles, AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

export interface ProgressStage {
  label: string;
  durationMs?: number;
}

interface StagedAIProgressIndicatorProps {
  stages: ProgressStage[];
  title?: string;
  subtitle?: string;
  error?: string | null;
  isFailed?: boolean;
  className?: string;
  onComplete?: () => void;
  onRetry?: () => void;
}

export function StagedAIProgressIndicator({
  stages,
  title = "AI Engine Active",
  subtitle = "Processing transparent multi-factor evaluation...",
  error,
  isFailed = false,
  className,
  onComplete,
  onRetry,
}: StagedAIProgressIndicatorProps) {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  useEffect(() => {
    if (isFailed || error) return;

    if (currentStageIndex >= stages.length) {
      onComplete?.();
      return;
    }

    const currentStage = stages[currentStageIndex];
    const duration = currentStage?.durationMs ?? 2500;

    const timer = setTimeout(() => {
      setCurrentStageIndex((prev) => prev + 1);
    }, duration);

    return () => clearTimeout(timer);
  }, [currentStageIndex, stages, isFailed, error, onComplete]);

  const hasError = isFailed || Boolean(error);

  return (
    <div
      className={cn(
        "glass-card p-6 rounded-2xl border space-y-5 text-center max-w-md mx-auto shadow-2xl animate-fade-in",
        hasError ? "border-destructive/40 bg-destructive/5" : "border-border/80",
        className
      )}
    >
      <div className="flex items-center justify-center gap-2">
        <div
          className={cn(
            "size-10 rounded-xl flex items-center justify-center border",
            hasError
              ? "bg-destructive/20 text-destructive border-destructive/30"
              : "bg-fuchsia-600/20 text-fuchsia-400 border-fuchsia-500/30 animate-pulse"
          )}
        >
          {hasError ? <AlertTriangle className="size-5" /> : <Sparkles className="size-5" />}
        </div>
      </div>

      <div className="space-y-1">
        <h4 className="text-base font-extrabold text-foreground">
          {hasError ? "AI Operation Error" : title}
        </h4>
        <p className="text-xs text-muted-foreground">
          {hasError
            ? error || "The AI processing engine encountered a timeout or invalid response."
            : subtitle}
        </p>
      </div>

      {/* Steps List */}
      <div className="space-y-2.5 pt-2 text-left">
        {stages.map((stage, idx) => {
          const isDone = idx < currentStageIndex && !hasError;
          const isCurrent = idx === currentStageIndex && !hasError;
          const isFailedStage = idx === currentStageIndex && hasError;
          const isPending = idx > currentStageIndex || (hasError && idx > currentStageIndex);

          return (
            <div
              key={idx}
              className={cn(
                "flex items-center gap-3 p-2.5 rounded-xl border transition-all text-xs font-semibold",
                isDone && "bg-emerald-500/10 border-emerald-500/20 text-emerald-300",
                isCurrent && "bg-fuchsia-500/15 border-fuchsia-500/30 text-fuchsia-300 shadow-sm",
                isFailedStage && "bg-destructive/15 border-destructive/30 text-destructive font-bold",
                isPending && "bg-secondary/40 border-border/40 text-muted-foreground/60"
              )}
            >
              {isDone && <CheckCircle2 className="size-4 text-emerald-400 shrink-0" />}
              {isCurrent && <Loader2 className="size-4 text-fuchsia-400 animate-spin shrink-0" />}
              {isFailedStage && <AlertTriangle className="size-4 text-destructive shrink-0" />}
              {isPending && !isFailedStage && (
                <div className="size-4 rounded-full border border-border/60 shrink-0" />
              )}
              <span className="truncate">
                {stage.label} {isFailedStage && "(Failed)"}
              </span>
            </div>
          );
        })}
      </div>

      {/* Error Recovery Action Button (Checklist Item #2) */}
      {hasError && onRetry && (
        <div className="pt-2">
          <Button
            onClick={onRetry}
            className="w-full h-10 rounded-xl bg-destructive hover:bg-destructive/90 text-white font-bold text-xs gap-2 shadow-md"
          >
            <RefreshCw className="size-3.5" />
            <span>Retry AI Operation</span>
          </Button>
        </div>
      )}
    </div>
  );
}
