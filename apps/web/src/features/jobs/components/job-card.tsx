/**
 * JobCard — display card for a posted job position.
 */

import { Briefcase, MapPin, Trash2, CheckCircle2, ChevronRight } from "lucide-react";
import { SkillTag } from "@/shared/design-system";
import { Button } from "@/shared/components/ui/button";
import type { Job } from "../types";
import { useDeleteJob } from "../hooks/use-jobs";
import { useAuthStore } from "@/features/auth/stores/auth-store";

interface JobCardProps {
  job: Job;
  onSelect?: (job: Job) => void;
}

export function JobCard({ job, onSelect }: JobCardProps) {
  const user = useAuthStore((s) => s.user);
  const deleteMutation = useDeleteJob();
  const isOwner = user?.id === job.created_by || user?.role === "admin";

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${job.title}"?`)) {
      deleteMutation.mutate(job.id);
    }
  };

  return (
    <div
      onClick={() => onSelect?.(job)}
      className="glass-card p-5 rounded-2xl border border-border shadow-md space-y-4 hover:border-fuchsia-500/50 transition-all cursor-pointer group relative overflow-hidden"
    >
      {/* Top Header & Badges */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-fuchsia-500/15 text-fuchsia-300 border border-fuchsia-500/20 uppercase tracking-wider">
              {job.department}
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground uppercase tracking-wider">
              {job.employment_type.replace("_", " ")}
            </span>
          </div>
          <h3 className="text-lg font-extrabold text-foreground group-hover:text-fuchsia-300 transition-colors">
            {job.title}
          </h3>
        </div>

        {isOwner && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="size-8 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="size-4" />
          </Button>
        )}
      </div>

      {/* Description Snippet */}
      <p className="text-xs font-medium text-foreground/80 line-clamp-2 leading-relaxed">
        {job.description}
      </p>

      {/* Meta Info: Location & Experience */}
      <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-foreground/75 pt-1">
        <div className="flex items-center gap-1.5">
          <MapPin className="size-3.5 text-fuchsia-400" />
          <span>{job.location}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Briefcase className="size-3.5 text-fuchsia-400" />
          <span>{job.min_experience_years}+ YOE Req.</span>
        </div>
      </div>

      {/* Required Skills Matrix */}
      <div className="pt-2 border-t border-border/40 space-y-1.5">
        <span className="text-[11px] font-bold text-foreground/70">Required Skills:</span>
        <div className="flex flex-wrap gap-1.5">
          {job.required_skills.slice(0, 5).map((skill, i) => (
            <SkillTag key={i} name={skill} status="matched" />
          ))}
          {job.required_skills.length > 5 && (
            <span className="text-[10px] font-bold text-muted-foreground self-center px-1">
              +{job.required_skills.length - 5} more
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 text-[11px] font-bold text-foreground/70">
        <div className="flex items-center gap-1">
          <CheckCircle2 className="size-3 text-emerald-400" />
          <span>Active Position</span>
        </div>
        <span className="text-fuchsia-400 group-hover:translate-x-0.5 transition-transform inline-flex items-center gap-0.5 font-bold">
          View Details <ChevronRight className="size-3" />
        </span>
      </div>
    </div>
  );
}
