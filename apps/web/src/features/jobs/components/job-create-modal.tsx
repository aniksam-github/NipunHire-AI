/**
 * JobCreateModal — modal form for recruiters to post new job openings.
 */

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, X, Sparkles } from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { jobFormSchema, type JobFormRawInput } from "../types";
import { useCreateJob } from "../hooks/use-jobs";

interface JobCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function JobCreateModal({ isOpen, onClose }: JobCreateModalProps) {
  const createJobMutation = useCreateJob();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<JobFormRawInput>({
    resolver: zodResolver(jobFormSchema),
    defaultValues: {
      title: "",
      description: "",
      department: "Engineering",
      location: "Bengaluru, India / Remote",
      employment_type: "full_time",
      min_experience_years: 2,
      required_skills: "FastAPI, React, TypeScript, MongoDB",
      optional_skills: "Docker, Tailwind CSS",
    },
  });

  if (!isOpen) return null;

  const onSubmit = (data: JobFormRawInput) => {
    const reqSkills = data.required_skills ? data.required_skills.split(",").map((s) => s.trim()).filter(Boolean) : [];
    const optSkills = data.optional_skills ? data.optional_skills.split(",").map((s) => s.trim()).filter(Boolean) : [];

    createJobMutation.mutate(
      {
        title: data.title,
        description: data.description,
        department: data.department,
        location: data.location,
        employment_type: data.employment_type,
        min_experience_years: Number(data.min_experience_years),
        required_skills: reqSkills,
        optional_skills: optSkills,
      },
      {
        onSuccess: () => {
          reset();
          onClose();
        },
      }
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md">
      <div className="w-full max-w-2xl glass-card rounded-2xl border border-border shadow-2xl p-6 space-y-6 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-fuchsia-600/20 text-fuchsia-400 border border-fuchsia-500/30">
              <Sparkles className="size-5" />
            </div>
            <div>
              <h3 className="text-xl font-extrabold text-foreground">Post New Job Opening</h3>
              <p className="text-xs font-semibold text-foreground/80">Specify position requirements for AI candidate matching</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="size-8 rounded-lg text-muted-foreground hover:text-foreground">
            <X className="size-5" />
          </Button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Job Title & Department */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Job Title</Label>
              <Input
                placeholder="Senior Full Stack Engineer"
                className="bg-background border-border text-foreground font-medium"
                {...register("title")}
              />
              {errors.title && <p className="text-xs font-semibold text-destructive">{errors.title.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Department</Label>
              <Input
                placeholder="Engineering"
                className="bg-background border-border text-foreground font-medium"
                {...register("department")}
              />
              {errors.department && <p className="text-xs font-semibold text-destructive">{errors.department.message}</p>}
            </div>
          </div>

          {/* Location & Employment Type & Min Experience */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Location</Label>
              <Input
                placeholder="Remote / Bengaluru"
                className="bg-background border-border text-foreground font-medium"
                {...register("location")}
              />
              {errors.location && <p className="text-xs font-semibold text-destructive">{errors.location.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Employment Type</Label>
              <select
                className="w-full h-9 px-3 rounded-xl bg-background border border-border text-foreground text-sm font-medium focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 outline-none"
                {...register("employment_type")}
              >
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Min YOE Required</Label>
              <Input
                type="number"
                placeholder="2"
                className="bg-background border-border text-foreground font-medium"
                {...register("min_experience_years", { valueAsNumber: true })}
              />
            </div>
          </div>

          {/* Required Skills (Comma Separated) */}
          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Required Skills (Comma Separated)</Label>
            <Input
              placeholder="FastAPI, React, TypeScript, MongoDB"
              className="bg-background border-border text-foreground font-medium"
              {...register("required_skills")}
            />
            <p className="text-[11px] font-semibold text-foreground/70">These skills are weighted heavily by Gemini AI for match scoring.</p>
          </div>

          {/* Optional Skills (Comma Separated) */}
          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Optional / Bonus Skills</Label>
            <Input
              placeholder="Docker, Tailwind CSS, PyMuPDF"
              className="bg-background border-border text-foreground font-medium"
              {...register("optional_skills")}
            />
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <Label className="text-xs font-bold uppercase tracking-wider text-foreground">Job Description & Responsibilities</Label>
            <textarea
              rows={4}
              placeholder="Provide job details, scope, and technical expectations..."
              className="w-full p-3 rounded-xl bg-background border border-border text-foreground text-sm font-medium placeholder:text-muted-foreground/90 focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-500/30 outline-none resize-none"
              {...register("description")}
            />
            {errors.description && <p className="text-xs font-semibold text-destructive">{errors.description.message}</p>}
          </div>

          {/* Submit Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
            <Button type="button" variant="outline" onClick={onClose} className="rounded-xl border-border text-foreground font-bold">
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createJobMutation.isPending}
              className="rounded-xl bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-bold gap-2 shadow-md"
            >
              {createJobMutation.isPending ? <Loader2 className="animate-spin size-4" /> : <Plus className="size-4" />}
              <span>Post Job Position</span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
