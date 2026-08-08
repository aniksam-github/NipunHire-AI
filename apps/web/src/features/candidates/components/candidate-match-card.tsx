/**
 * CandidateMatchCard — detailed evaluation scorecard displaying ATS match breakdown,
 * skill gaps, readiness score, and AI recommendations.
 */

import { Sparkles, CheckCircle2, AlertTriangle, Lightbulb, Target } from "lucide-react";
import { ATSBadge, SkillTag, ConfidenceMeter } from "@/shared/design-system";
import type { MatchResponse } from "../types";

interface CandidateMatchCardProps {
  match: MatchResponse;
  jobTitle?: string;
}

export function CandidateMatchCard({ match, jobTitle }: CandidateMatchCardProps) {
  return (
    <div className="glass-card p-6 rounded-2xl border border-border shadow-xl space-y-6">
      {/* Top Banner: Match Score & Application Readiness */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-fuchsia-500/20 text-fuchsia-300 font-mono uppercase tracking-wider">
              Gemini AI Evaluation
            </span>
            {jobTitle && (
              <span className="text-xs font-semibold text-foreground/80">
                Position: <span className="font-bold text-foreground">{jobTitle}</span>
              </span>
            )}
          </div>
          <h3 className="text-xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Candidate Evaluation Breakdown</span>
            <Sparkles className="size-5 text-fuchsia-400" />
          </h3>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Application Readiness</p>
            <p className="text-lg font-extrabold text-foreground">{match.application_readiness_score}%</p>
          </div>
          <ATSBadge score={match.match_score} className="text-sm px-4 py-2" />
        </div>
      </div>

      {/* Confidence Meter Bar */}
      <ConfidenceMeter score={match.match_score} label="AI Match Suitability Index" />

      {/* Matched vs Missing Skill Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Skills */}
        <div className="p-4 rounded-xl bg-background border border-border/80 space-y-3">
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-foreground flex items-center gap-1.5">
            <CheckCircle2 className="size-4 text-emerald-400" />
            <span>Matched Requirements ({match.matched_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {match.matched_skills.length > 0 ? (
              match.matched_skills.map((skill, i) => (
                <SkillTag key={i} name={skill} status="matched" />
              ))
            ) : (
              <p className="text-xs font-semibold text-foreground/70">No direct skills matched.</p>
            )}
          </div>
        </div>

        {/* Missing Required Skills */}
        <div className="p-4 rounded-xl bg-background border border-border/80 space-y-3">
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-foreground flex items-center gap-1.5">
            <AlertTriangle className="size-4 text-rose-400" />
            <span>Missing Required Skills ({match.missing_required_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {match.missing_required_skills.length > 0 ? (
              match.missing_required_skills.map((skill, i) => (
                <SkillTag key={i} name={skill} status="missing" />
              ))
            ) : (
              <span className="text-xs font-bold text-emerald-400">All required skills present!</span>
            )}
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-semibold">
        <div className="p-4 rounded-xl bg-secondary/60 border border-border/60 space-y-2">
          <p className="font-bold text-foreground flex items-center gap-1.5">
            <Target className="size-4 text-fuchsia-400" />
            <span>Verified Candidate Strengths</span>
          </p>
          <ul className="space-y-1 text-foreground/80 list-disc list-inside">
            {match.strengths.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="p-4 rounded-xl bg-secondary/60 border border-border/60 space-y-2">
          <p className="font-bold text-foreground flex items-center gap-1.5">
            <AlertTriangle className="size-4 text-amber-400" />
            <span>Growth Areas & Missing Criteria</span>
          </p>
          <ul className="space-y-1 text-foreground/80 list-disc list-inside">
            {match.weaknesses.length > 0 ? (
              match.weaknesses.map((item, i) => <li key={i}>{item}</li>)
            ) : (
              <li>No major skill deficits identified.</li>
            )}
          </ul>
        </div>
      </div>

      {/* AI Recommendations Box */}
      {match.recommendations.length > 0 && (
        <div className="p-4 rounded-xl bg-fuchsia-600/10 border border-fuchsia-500/30 space-y-2 text-xs font-semibold">
          <p className="font-bold text-fuchsia-300 flex items-center gap-1.5">
            <Lightbulb className="size-4 text-amber-400" />
            <span>AI Actionable Recommendations for Candidate</span>
          </p>
          <ul className="space-y-1 text-foreground/90 list-disc list-inside">
            {match.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
