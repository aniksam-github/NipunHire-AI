import { useEffect, useState } from "react";
import { Loader2, Send, Sparkles, AlertTriangle, Cpu, HardDrive } from "lucide-react";
import { toast } from "sonner";

import { codingApi } from "@/shared/lib/api-client";
import { HumanDecisionTrustBadge } from "@/shared/design-system";
import type { CodingQuestion, ConsolidatedCodingFeedbackResponse } from "@/shared/types/coding";
import { Button } from "@/shared/components/ui/button";

export function CodingPracticePage() {
  const [questions, setQuestions] = useState<CodingQuestion[]>([]);
  const [selected, setSelected] = useState<CodingQuestion | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<"python" | "javascript" | "typescript" | "java" | "cpp" | "sql" | "go">("python");
  const [result, setResult] = useState<ConsolidatedCodingFeedbackResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [targetJobId, setTargetJobId] = useState("");
  const [targetDifficulty, setTargetDifficulty] = useState<"easy" | "medium" | "hard">("medium");

  useEffect(() => {
    // Load default questions
    codingApi
      .getConsolidatedFeedback("two-sum-python")
      .catch(() => null);

    const defaultQuestions: CodingQuestion[] = [
      {
        id: "two-sum-python",
        title: "Two Sum",
        problem_statement: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        difficulty: "easy",
        starter_code: "def two_sum(nums, target):\n    # Write your solution here\n    pass",
      },
      {
        id: "sql-active-users",
        title: "Active Users Query",
        problem_statement: "Write a SQL query returning users who have logged in during the last 30 days.",
        difficulty: "easy",
        starter_code: "SELECT user_id, email\nFROM users\nWHERE last_login >= NOW() - INTERVAL '30 days';",
      },
    ];
    setQuestions(defaultQuestions);
    setSelected(defaultQuestions[0]);
    setCode(defaultQuestions[0].starter_code || "");
    setLoading(false);
  }, []);

  const choose = (question: CodingQuestion) => {
    setSelected(question);
    setCode(question.starter_code || "");
    setResult(null);
  };

  const handleGenerateQuestion = async () => {
    if (!targetJobId.trim()) {
      toast.error("Please enter a valid Job ID to tailor the coding challenge");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await codingApi.generateQuestion({
        job_id: targetJobId.trim(),
        difficulty: targetDifficulty,
      });
      setQuestions((prev) => [res.question, ...prev]);
      setSelected(res.question);
      setCode(res.question.starter_code || "");
      setResult(null);
      toast.success(`AI Coding Challenge generated: ${res.question.title}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to generate AI coding question");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmitCode = async () => {
    if (!selected || !code.trim()) return;
    setSubmitting(true);
    try {
      const feedback = await codingApi.submitCodeForReview({
        question_id: selected.id,
        language,
        code: code.trim(),
      });
      setResult(feedback);
      toast.success("Static AI Code Review completed!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to analyze submitted code");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6">
      {/* Mandatory Human Decision Support Trust Badge (Checklist #11) */}
      <HumanDecisionTrustBadge message="AI Code Review feedback (Big-O analysis, edge case checks, syntax validation) is an explainable decision-support signal. Code is statically analyzed without sandbox execution." />

      {/* Header Banner */}
      <div className="glass-card p-6 sm:p-8 rounded-3xl border border-border/60 bg-gradient-to-r from-emerald-950/20 via-background to-cyan-950/20 relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
              <Sparkles className="size-3.5" />
              <span>Phase 7 — AI Static Code Review & Complexity Analysis</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
              Coding Challenge & Code Quality Studio
            </h1>
            <p className="text-sm text-muted-foreground max-w-2xl">
              Submit solution code for static AI review assessing logical correctness, edge cases/bugs, syntax validity, and Big-O time & space complexity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
