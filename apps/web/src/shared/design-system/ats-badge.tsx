/**
 * ATSBadge — candidate match score indicator badge.
 *
 * Visual tiers:
 *   - High Match (>= 80%): Emerald green glow
 *   - Medium Match (50% - 79%): Amber gold glow
 *   - Low Match (< 50%): Rose red indicator
 */

import { cn } from "@/shared/lib/utils";
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";

interface ATSBadgeProps {
  score: number; // 0 - 100
  className?: string;
  showIcon?: boolean;
}

export function ATSBadge({ score, className, showIcon = true }: ATSBadgeProps) {
  let tierStyle = "bg-rose-500/15 text-rose-300 border-rose-500/30";
  let Icon = XCircle;
  let label = "Low Match";

  if (score >= 80) {
    tierStyle = "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
    Icon = CheckCircle2;
    label = "High Match";
  } else if (score >= 50) {
    tierStyle = "bg-amber-500/15 text-amber-300 border-amber-500/30";
    Icon = AlertCircle;
    label = "Fair Match";
  }

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-bold tracking-wide shadow-sm",
        tierStyle,
        className
      )}
    >
      {showIcon && <Icon className="size-3.5" />}
      <span>{score}% {label}</span>
    </div>
  );
}
