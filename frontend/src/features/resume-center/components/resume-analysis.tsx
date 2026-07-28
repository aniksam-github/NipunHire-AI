/**
 * ResumeAnalysis — detailed ATS Resume Health Scorecard & AI Quality Feedback view.
 */

import { CheckCircle2, AlertTriangle, Lightbulb, Mail, Phone, Cpu, FileCheck } from "lucide-react";
import { ATSBadge, SkillTag, ConfidenceMeter } from "@/shared/design-system";
import type { Resume } from "../types";

interface ResumeAnalysisProps {
  resume: Resume;
}

export function ResumeAnalysis({ resume }: ResumeAnalysisProps) {
  const { quality_breakdown, ai_feedback } = resume;

  return (
    <div className="space-y-6">
      {/* ATS Overall Score Header Banner */}
      <div className="glass-card p-6 rounded-2xl border border-border shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-fuchsia-500/20 text-fuchsia-300 font-mono uppercase">
                {resume.filename}
              </span>
              <span className="text-xs font-semibold text-foreground/70">
                {resume.page_count} Page{resume.page_count > 1 ? "s" : ""} • {(resume.file_size_bytes / 1024).toFixed(1)} KB
              </span>
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight text-foreground">
              ATS Resume Health Scorecard
            </h2>
          </div>
          <ATSBadge score={resume.ats_score} className="text-sm px-4 py-2" />
        </div>

        <ConfidenceMeter score={resume.ats_score} label="Overall ATS Compatibility Index" />
      </div>

      {/* 3 Quality Sub-Scores Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Contact Completeness
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.completeness_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Email & Phone verification</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Keyword Density
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.keyword_density_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Extracted tech skills count</p>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-border space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Formatting & Structure
          </span>
          <div className="text-2xl font-extrabold text-foreground">
            {quality_breakdown.formatting_score}%
          </div>
          <p className="text-xs font-semibold text-foreground/70">Page count & text density</p>
        </div>
      </div>

      {/* Contact Info & Extracted Tech Skills Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Parsed Contact Info */}
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
          <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
            <FileCheck className="size-4 text-fuchsia-400" />
            <span>Parsed Contact Attributes</span>
          </h3>

          <div className="space-y-3 text-xs font-semibold">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-background border border-border/60">
              <Mail className="size-4 text-fuchsia-400" />
              <div>
                <p className="text-foreground/70 text-[10px]">Extracted Email</p>
                <p className="text-foreground font-bold">{resume.parsed_email ?? "Not Detected"}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-background border border-border/60">
              <Phone className="size-4 text-fuchsia-400" />
              <div>
                <p className="text-foreground/70 text-[10px]">Extracted Phone</p>
                <p className="text-foreground font-bold">{resume.parsed_phone ?? "Not Detected"}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Extracted Skills Matrix */}
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
          <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
            <Cpu className="size-4 text-fuchsia-400" />
            <span>Extracted Technical Skills ({resume.extracted_skills.length})</span>
          </h3>

          <div className="flex flex-wrap gap-1.5 pt-1">
            {resume.extracted_skills.length > 0 ? (
              resume.extracted_skills.map((skill, i) => (
                <SkillTag key={i} name={skill} status="matched" />
              ))
            ) : (
              <p className="text-xs font-semibold text-foreground/70">No standard tech skills detected in text.</p>
            )}
          </div>
        </div>
      </div>

      {/* AI Suggestions & Improvements Box */}
      <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
          <Lightbulb className="size-5 text-amber-400" />
          <span>AI Resume Quality Recommendations</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-semibold">
          {/* Missing / Recommended Elements */}
          <div className="p-4 rounded-xl bg-background border border-border/60 space-y-2">
            <p className="font-bold text-foreground flex items-center gap-1.5">
              <AlertTriangle className="size-4 text-amber-400" />
              <span>Missing & Recommended Keywords</span>
            </p>
            <ul className="space-y-1 text-foreground/80 list-disc list-inside">
              {ai_feedback.missing_elements.length > 0 ? (
                ai_feedback.missing_elements.map((item, i) => <li key={i}>{item}</li>)
              ) : (
                <li>No critical elements missing! Great job.</li>
              )}
            </ul>
          </div>

          {/* Action Verbs */}
          <div className="p-4 rounded-xl bg-background border border-border/60 space-y-2">
            <p className="font-bold text-foreground flex items-center gap-1.5">
              <CheckCircle2 className="size-4 text-emerald-400" />
              <span>High-Impact Action Verbs to Include</span>
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {ai_feedback.action_verb_suggestions.map((verb, i) => (
                <span key={i} className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[11px] font-bold">
                  {verb}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
