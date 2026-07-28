/**
 * SkillTag — technology stack badge component.
 *
 * Types:
 *   - matched: Verified skill matching job requirements (emerald accent)
 *   - missing: Required skill missing from candidate resume (rose/amber accent)
 *   - neutral: General candidate skill tag (fuchsia/lavender accent)
 */

import { cn } from "@/shared/lib/utils";
import { Check, X } from "lucide-react";

interface SkillTagProps {
  name: string;
  status?: "matched" | "missing" | "neutral";
  className?: string;
}

export function SkillTag({ name, status = "neutral", className }: SkillTagProps) {
  let statusStyle = "bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-500/25";

  if (status === "matched") {
    statusStyle = "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
  } else if (status === "missing") {
    statusStyle = "bg-rose-500/15 text-rose-300 border-rose-500/30";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md border text-[11px] font-semibold tracking-wide shadow-xs",
        statusStyle,
        className
      )}
    >
      {status === "matched" && <Check className="size-3 text-emerald-400" />}
      {status === "missing" && <X className="size-3 text-rose-400" />}
      <span>{name}</span>
    </span>
  );
}
