/**
 * ConfidenceMeter — visual percentage bar for AI match & confidence score.
 */

import { cn } from "@/shared/lib/utils";

interface ConfidenceMeterProps {
  score: number; // 0 - 100
  label?: string;
  className?: string;
}

export function ConfidenceMeter({ score, label, className }: ConfidenceMeterProps) {
  let barColor = "bg-rose-500";
  let textColor = "text-rose-400";

  if (score >= 80) {
    barColor = "bg-emerald-500";
    textColor = "text-emerald-400";
  } else if (score >= 50) {
    barColor = "bg-amber-500";
    textColor = "text-amber-400";
  }

  return (
    <div className={cn("space-y-1.5 w-full", className)}>
      <div className="flex justify-between items-center text-xs font-bold">
        <span className="text-foreground">{label ?? "Match Score"}</span>
        <span className={textColor}>{score}%</span>
      </div>
      <div className="h-2 w-full bg-secondary rounded-full overflow-hidden p-0.5 border border-border/40">
        <div
          className={cn("h-full rounded-full transition-all duration-500", barColor)}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  );
}
