/**
 * HumanDecisionTrustBadge — mandatory visual indicator framing AI outputs
 * strictly as explainable decision-support signals for human evaluation (Checklist #11).
 */

import { ShieldCheck } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface HumanDecisionTrustBadgeProps {
  className?: string;
  compact?: boolean;
  message?: string;
}

export function HumanDecisionTrustBadge({
  className,
  compact = false,
  message = "Human-in-the-Loop AI Directive: This evaluation is an explainable decision-support signal. Final hiring & screening decisions are always made by human evaluators.",
}: HumanDecisionTrustBadgeProps) {
  if (compact) {
    return (
      <div
        className={cn(
          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-sky-500/10 border border-sky-500/20 text-[11px] font-semibold text-sky-300",
          className
        )}
      >
        <ShieldCheck className="size-3.5 text-sky-400 shrink-0" />
        <span>Decision-Support Signal</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3.5 rounded-xl bg-sky-500/10 border border-sky-500/25 text-xs text-sky-200 font-medium leading-relaxed",
        className
      )}
    >
      <ShieldCheck className="size-4 text-sky-400 shrink-0 mt-0.5" />
      <div className="flex-1">
        <span className="font-bold text-sky-300 mr-1.5">
          Human-in-the-Loop AI Directive:
        </span>
        <span className="text-sky-200/90">{message}</span>
      </div>
    </div>
  );
}
