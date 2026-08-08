/**
 * GuidedNextStepCard — prominent next-step CTA chain with mandatory easy exit & dismissal persistence (Rule #3, #4, Checklist #13).
 * Guides users along the recommended workflow while ensuring they never feel trapped.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles, XCircle } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

interface GuidedNextStepCardProps {
  title: string;
  description: string;
  actionLabel: string;
  actionPath: string;
  exitPath?: string;
  exitLabel?: string;
  dismissibleKey?: string;
  icon?: React.ReactNode;
  className?: string;
  onDismiss?: () => void;
}

export function GuidedNextStepCard({
  title,
  description,
  actionLabel,
  actionPath,
  exitPath = "/dashboard",
  exitLabel = "Not now, return to Dashboard",
  dismissibleKey,
  icon = <Sparkles className="size-5 text-fuchsia-400" />,
  className,
  onDismiss,
}: GuidedNextStepCardProps) {
  const navigate = useNavigate();
  const [isDismissed, setIsDismissed] = useState(() => {
    if (dismissibleKey) {
      return localStorage.getItem(dismissibleKey) === "true";
    }
    return false;
  });

  if (isDismissed) {
    return null;
  }

  const handleExit = () => {
    if (dismissibleKey) {
      localStorage.setItem(dismissibleKey, "true");
    }
    setIsDismissed(true);
    if (onDismiss) {
      onDismiss();
    }
    if (exitPath) {
      navigate(exitPath);
    }
  };

  return (
    <div
      className={cn(
        "glass-card p-6 rounded-2xl border border-fuchsia-500/30 bg-gradient-to-r from-fuchsia-950/20 via-background to-purple-950/20 shadow-xl space-y-4 animate-fade-in",
        className
      )}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="size-10 rounded-xl bg-fuchsia-500/15 border border-fuchsia-500/30 flex items-center justify-center shrink-0">
            {icon}
          </div>
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 text-[10px] font-extrabold uppercase tracking-wider text-fuchsia-400">
              <span>Recommended Next Action</span>
            </div>
            <h3 className="text-base font-extrabold text-foreground">{title}</h3>
            <p className="text-xs text-muted-foreground max-w-xl">{description}</p>
          </div>
        </div>

        {/* Action Buttons: Primary Forward CTA + Persistent Easy Exit */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
          <Button
            onClick={() => navigate(actionPath)}
            className="h-10 rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold text-xs shadow-md gap-2 px-5"
          >
            <span>{actionLabel}</span>
            <ArrowRight className="size-4" />
          </Button>

          <Button
            onClick={handleExit}
            variant="ghost"
            className="h-10 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent font-semibold text-xs gap-1.5 px-4"
          >
            <XCircle className="size-3.5" />
            <span>{exitLabel}</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
