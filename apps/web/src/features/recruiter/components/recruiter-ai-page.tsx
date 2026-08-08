import { useState } from "react";
import {
  Users,
  Sparkles,
  Award,
  Sliders,
  FileText,
  Loader2,
  TrendingUp,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import { HumanDecisionTrustBadge } from "@/shared/design-system";

import { recruiterApi } from "@/shared/lib/api-client";
import type {
  CandidateComparisonResult,
  CandidateRankingList,
  AggregateHiringRecommendationResponse,
  GeneratedJobDescription,
} from "@/shared/types/recruiter";

export function RecruiterAIPage() {
  const [jobIdInput, setJobIdInput] = useState("");
  const [candidateIdsInput, setCandidateIdsInput] = useState("");
  const [activeTab, setActiveTab] = useState<"ranking" | "comparison" | "recommendation" | "jd">("ranking");

  // State for modules
  const [rankingData, setRankingData] = useState<CandidateRankingList | null>(null);
  const [comparisonData, setComparisonData] = useState<CandidateComparisonResult | null>(null);
  const [recommendationData, setRecommendationData] = useState<AggregateHiringRecommendationResponse | null>(null);
  const [generatedJd, setGeneratedJd] = useState<GeneratedJobDescription | null>(null);

  // Weights state
  const [matchWeight, setMatchWeight] = useState(0.4);
  const [interviewWeight, setInterviewWeight] = useState(0.35);
  const [codingWeight, setCodingWeight] = useState(0.25);

  const [loading, setLoading] = useState(false);

  // JD Form state
  const [jdRoleTitle, setJdRoleTitle] = useState("");
  const [jdSkills, setJdSkills] = useState("");
  const [jdSeniority, setJdSeniority] = useState("Senior");

  const handleRankCandidates = async () => {
    if (!jobIdInput.trim()) {
      toast.error("Please enter a valid Job ID");
      return;
    }
    setLoading(true);
    try {
      const cIds = candidateIdsInput.trim() ? candidateIdsInput.split(",").map((s) => s.trim()) : undefined;
      const res = await recruiterApi.rankCandidates(jobIdInput.trim(), cIds, {
        match_weight: matchWeight,
        interview_weight: interviewWeight,
        coding_weight: codingWeight,
      });
      setRankingData(res);
      toast.success(`Candidates ranked for Job #${jobIdInput}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to rank candidates");
    } finally {
      setLoading(false);
    }
  };

  const handleCompareCandidates = async () => {
    if (!jobIdInput.trim() || !candidateIdsInput.trim()) {
      toast.error("Please enter Job ID and at least 2 comma-separated Candidate IDs");
      return;
    }
    const ids = candidateIdsInput.split(",").map((s) => s.trim()).filter(Boolean);
    if (ids.length < 2) {
      toast.error("Candidate comparison requires at least 2 candidate IDs");
      return;
    }
    setLoading(true);
    try {
      const res = await recruiterApi.compareCandidates({
        job_id: jobIdInput.trim(),
        candidate_ids: ids,
      });
      setComparisonData(res);
      toast.success("Side-by-side candidate comparison generated");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to compare candidates");
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendation = async () => {
    const cId = candidateIdsInput.trim().split(",")[0]?.trim();
    if (!cId) {
      toast.error("Please enter a Candidate ID");
      return;
    }
    setLoading(true);
    try {
      const res = await recruiterApi.getAggregateRecommendation(cId, jobIdInput.trim() || undefined);
      setRecommendationData(res);
      toast.success("Aggregate hiring recommendation generated");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to generate aggregate recommendation");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateJd = async () => {
    if (!jdRoleTitle.trim() || !jdSkills.trim()) {
      toast.error("Please enter Role Title and Skills");
      return;
    }
    setLoading(true);
    try {
      const res = await recruiterApi.generateJobDescription({
        role_title: jdRoleTitle.trim(),
        required_skills: jdSkills.split(",").map((s) => s.trim()),
        seniority_level: jdSeniority,
      });
      setGeneratedJd(res);
      toast.success(`Job Description generated for ${res.role_title}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to generate Job Description");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-4 sm:p-6">
      {/* Mandatory Human Decision Support Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="All candidate rankings, side-by-side matrices, and AI rank justifications are decision-support signals designed to assist recruiter shortlisting. Automated systems never issue independent employment decisions." />

      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-border/60 bg-gradient-to-r from-fuchsia-950/20 via-background to-purple-950/20 relative overflow-hidden">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 text-xs font-semibold">
            <Sparkles className="size-3.5" />
            <span>Phase 8 — Recruiter AI & Decision Support</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            Recruiter Candidate Intelligence Studio
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Rank applicants deterministically using sub-score weighting, generate side-by-side comparison matrices, and auto-generate structured job descriptions with AI reasoning.
          </p>
        </div>
      </div>
    </div>
  );
}
