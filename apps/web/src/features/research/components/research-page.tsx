import { useState } from "react";
import {
  Brain,
  FileSearch,
  AlertOctagon,
  BarChart3,
  Info,
} from "lucide-react";
import { toast } from "sonner";

import { researchApi } from "@/shared/lib/api-client";
import { HumanDecisionTrustBadge } from "@/shared/design-system";
import type {
  ExplanationTraceResponse,
  ProcessBiasAuditResponse,
  ResumeAnomalyCheckResponse,
  InterviewCheatRiskResponse,
} from "@/shared/types/research";

export function ResearchPage() {
  const [jobId, setJobId] = useState("");
  const [candidateId, setCandidateId] = useState("");
  const [resumeId, setResumeId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [activeTab, setActiveTab] = useState<"trace" | "bias" | "resume" | "cheat">("trace");

  // State for modules
  const [traceData, setTraceData] = useState<ExplanationTraceResponse | null>(null);
  const [biasData, setBiasData] = useState<ProcessBiasAuditResponse | null>(null);
  const [resumeData, setResumeData] = useState<ResumeAnomalyCheckResponse | null>(null);
  const [cheatData, setCheatData] = useState<InterviewCheatRiskResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const handleFetchTrace = async () => {
    if (!candidateId.trim() || !jobId.trim()) {
      toast.error("Please enter Candidate ID and Job ID");
      return;
    }
    setLoading(true);
    try {
      const res = await researchApi.getExplanationTrace(candidateId.trim(), jobId.trim());
      setTraceData(res);
      toast.success("Unified Explanation Trace generated");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to fetch explanation trace");
    } finally {
      setLoading(false);
    }
  };

  const handleAuditProcessBias = async () => {
    if (!jobId.trim()) {
      toast.error("Please enter Job ID");
      return;
    }
    setLoading(true);
    try {
      const res = await researchApi.auditProcessBias(jobId.trim());
      setBiasData(res);
      toast.success("Statistical Process Bias Audit completed (Zero Demographic Data)");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to perform bias audit");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckResumeAnomalies = async () => {
    if (!candidateId.trim() || !resumeId.trim()) {
      toast.error("Please enter Candidate ID and Resume ID");
      return;
    }
    setLoading(true);
    try {
      const res = await researchApi.checkResumeAnomalies(candidateId.trim(), resumeId.trim());
      setResumeData(res);
      toast.success("Resume Internal Consistency Audit completed");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to audit resume anomalies");
    } finally {
      setLoading(false);
    }
  };

  const handleDetectCheatRisk = async () => {
    if (!candidateId.trim() || !sessionId.trim()) {
      toast.error("Please enter Candidate ID and Session ID");
      return;
    }
    setLoading(true);
    try {
      const res = await researchApi.detectCheatRisk(candidateId.trim(), sessionId.trim());
      setCheatData(res);
      toast.success("Interview Stylometric Anomaly Detection completed");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to detect interview cheat risk");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-4 sm:p-6">
      {/* Mandatory Human Decision Support Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="All research outputs, stylometric cheat risk flags, and statistical process audits are explainable decision-support signals. Automated systems never auto-disqualify candidates." />

      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-border/60 bg-gradient-to-r from-blue-950/20 via-background to-cyan-950/20 relative overflow-hidden">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-semibold">
            <Brain className="size-3.5" />
            <span>Phase 9 — Research Features & Algorithmic Ethics</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            Academic Research & Decision-Support Studio
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Unified multi-phase explanation tracing, statistical process-level bias auditing (zero demographic profiling), resume internal consistency checks, and interview stylometric monitoring.
          </p>
        </div>
      </div>
    </div>
  );
}
