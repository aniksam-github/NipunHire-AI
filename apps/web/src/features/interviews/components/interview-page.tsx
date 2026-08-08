import { useState } from "react";
import {
  Sparkles,
  Play,
  Send,
  CheckCircle2,
  AlertCircle,
  Award,
  Brain,
  MessageSquare,
  BarChart2,
} from "lucide-react";
import { toast } from "sonner";

import { interviewApi } from "@/shared/lib/api-client";
import { HumanDecisionTrustBadge } from "@/shared/design-system";
import type { InterviewSession, InterviewTurn, InterviewReport } from "@/shared/types/interview";

export function InterviewPage() {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [activeTurn, setActiveTurn] = useState<InterviewTurn | null>(null);
  const [answerInput, setAnswerInput] = useState("");
  const [isStarting, setIsStarting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [finalReport, setFinalReport] = useState<InterviewReport | null>(null);

  const handleStartSession = async () => {
    setIsStarting(true);
    try {
      const sess = await interviewApi.startSession({ difficulty: selectedDifficulty });
      setSession(sess);
      setFinalReport(null);
      toast.success(`Adaptive Interview session started (${selectedDifficulty.toUpperCase()} level)`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to start interview session");
    } finally {
      setIsStarting(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !answerInput.trim()) return;
    setIsSubmitting(true);
    try {
      const turn = await interviewApi.submitTurn(session.id, { candidate_answer: answerInput.trim() });
      setActiveTurn(turn);
      const updatedSess = await interviewApi.getSession(session.id);
      setSession(updatedSess);
      setAnswerInput("");
      toast.success(`Turn #${turn.turn_index + 1} evaluated successfully`);

      if (updatedSess.status === "ready_to_complete" || updatedSess.status === "completed") {
        const report = await interviewApi.completeSession(session.id);
        setFinalReport(report);
        toast.info("Interview session completed! Final report generated.");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to evaluate answer turn");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-4 sm:p-6">
      {/* Mandatory Human Decision Support Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="AI Interview scores, difficulty shifts, and 5-dimension turn evaluations are explainable practice signals designed for candidate self-evaluation and recruiter decision support." />

      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-border/60 bg-gradient-to-r from-fuchsia-900/20 via-background to-purple-900/20 relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 text-xs font-semibold">
              <Sparkles className="size-3.5" />
              <span>Phase 6 — Adaptive AI Interview Simulator</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
              Interactive AI Technical Interview
            </h1>
            <p className="text-sm text-muted-foreground max-w-2xl">
              Experience multi-turn adaptive interviewing with real-time 5-dimension scoring, dynamic difficulty shifts, and comprehensive performance benchmark reports.
            </p>
          </div>

          {!session && (
            <div className="flex items-center gap-3">
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value as any)}
                className="bg-card text-foreground border border-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-fuchsia-500"
              >
                <option value="easy">Easy Level</option>
                <option value="medium">Medium Level</option>
                <option value="hard">Hard Level</option>
              </select>
              <button
                onClick={handleStartSession}
                disabled={isStarting}
                className="flex items-center gap-2 bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md disabled:opacity-50"
              >
                <Play className="size-4 fill-white" />
                <span>{isStarting ? "Starting..." : "Start Interview"}</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Active Session & Turn View */}
      {session && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Interview Q&A Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status & Progress Bar */}
            <div className="glass-card p-4 rounded-2xl border border-border/60 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Session Status:</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20">
                  {session.status.replace("_", " ").toUpperCase()}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
                <span>Turn {session.turns.length} of {session.max_questions}</span>
                <span className="px-2 py-0.5 rounded-md bg-card border border-border text-foreground font-mono">
                  Difficulty: {session.current_difficulty.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Current Turn Question Box */}
            {session.status === "in_progress" && (
              <div className="glass-card p-6 rounded-3xl border border-border/60 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="size-5 text-fuchsia-400" />
                    <h3 className="text-lg font-bold text-foreground">Current Question</h3>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-lg bg-card border border-border text-muted-foreground">
                    Category: Technical
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-fuchsia-950/20 border border-fuchsia-500/20 text-foreground text-sm font-medium leading-relaxed">
                  {(() => {
                    if (session.turns.length === 0) return "Initializing question sequence...";
                    const q = session.turns[session.turns.length - 1].question;
                    return typeof q === "string" ? q : q?.question_text || "";
                  })()}
                </div>

                <div className="space-y-3 pt-2">
                  <label className="text-xs font-semibold text-muted-foreground">Your Answer / Response:</label>
                  <textarea
                    rows={5}
                    value={answerInput}
                    onChange={(e) => setAnswerInput(e.target.value)}
                    placeholder="Type your response with technical details, architecture decisions, and code examples..."
                    className="w-full bg-card text-foreground border border-border rounded-2xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-fuchsia-500 resize-none"
                  />
                  <div className="flex justify-end">
                    <button
                      onClick={handleSubmitAnswer}
                      disabled={isSubmitting || !answerInput.trim()}
                      className="flex items-center gap-2 bg-fuchsia-600 hover:bg-fuchsia-700 text-white font-semibold px-6 py-2.5 rounded-xl transition-all shadow-md disabled:opacity-50"
                    >
                      <Send className="size-4" />
                      <span>{isSubmitting ? "Evaluating..." : "Submit Response"}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Turn History Timeline */}
            <div className="glass-card p-6 rounded-3xl border border-border/60 space-y-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="size-5 text-fuchsia-400" />
                <h3 className="text-lg font-bold text-foreground">Interview Turn History ({session.turns.length})</h3>
              </div>

              <div className="space-y-4">
                {session.turns.map((turn, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-card border border-border/60 space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-muted-foreground">
                      <span>Turn #{turn.turn_index + 1}</span>
                      <span className="text-fuchsia-400">Score: {turn.evaluation.overall_turn_score}%</span>
                    </div>
                    <p className="text-xs text-foreground font-medium">
                      Q: {typeof turn.question === "string" ? turn.question : turn.question?.question_text}
                    </p>
                    <p className="text-xs text-muted-foreground italic">A: {turn.candidate_answer}</p>
                    <div className="p-3 rounded-xl bg-background border border-border/40 text-[11px] text-muted-foreground">
                      <strong className="text-foreground">AI Feedback:</strong> {turn.evaluation.evaluation_reasoning}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Side Performance Overview */}
          <div className="space-y-6">
            <div className="glass-card p-6 rounded-3xl border border-border/60 space-y-4">
              <div className="flex items-center gap-2">
                <Award className="size-5 text-fuchsia-400" />
                <h3 className="text-lg font-bold text-foreground">Session Metrics</h3>
              </div>
              <div className="space-y-3 text-sm font-semibold">
                <div className="flex justify-between p-3 rounded-xl bg-card border border-border">
                  <span className="text-muted-foreground">Turns Completed:</span>
                  <span className="text-foreground">{session.turns.length}</span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-card border border-border">
                  <span className="text-muted-foreground">Current Level:</span>
                  <span className="text-fuchsia-400 capitalize">{session.current_difficulty}</span>
                </div>
                <div className="flex justify-between p-3 rounded-xl bg-card border border-border">
                  <span className="text-muted-foreground">Max Questions:</span>
                  <span className="text-foreground">{session.max_questions}</span>
                </div>
              </div>
            </div>

            {/* Final Report Card */}
            {finalReport && (
              <div className="glass-card p-6 rounded-3xl border border-fuchsia-500/30 bg-fuchsia-950/10 space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="size-5 text-emerald-400" />
                  <h3 className="text-lg font-bold text-foreground">Final Report</h3>
                </div>
                <div className="text-3xl font-extrabold text-fuchsia-400">
                  {finalReport.overall_score}%
                </div>
                <p className="text-xs text-muted-foreground">{finalReport.summary_assessment}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
