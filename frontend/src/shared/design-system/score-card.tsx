/**
 * ScoreCard — metric summary KPI card for recruiter overview.
 */

import { type ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

interface ScoreCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: ReactNode;
  trend?: string;
  className?: string;
}

export function ScoreCard({
  title,
  value,
  description,
  icon,
  trend,
  className,
}: ScoreCardProps) {
  return (
    <div
      className={cn(
        "glass-card p-5 rounded-2xl border border-border shadow-lg space-y-3 relative overflow-hidden",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
        <div className="p-2.5 rounded-xl bg-fuchsia-600/15 text-fuchsia-400 border border-fuchsia-500/20">
          {icon}
        </div>
      </div>

      <div className="space-y-1">
        <div className="text-3xl font-extrabold tracking-tight text-foreground">
          {value}
        </div>
        {description && (
          <p className="text-xs font-medium text-foreground/80">{description}</p>
        )}
      </div>

      {trend && (
        <div className="text-[11px] font-bold text-emerald-400 pt-1 border-t border-border/40">
          {trend}
        </div>
      )}
    </div>
  );
}
