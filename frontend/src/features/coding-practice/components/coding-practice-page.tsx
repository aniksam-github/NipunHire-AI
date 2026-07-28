import { useEffect, useState } from "react";
import { Code2, Loader2, Send } from "lucide-react";
import { api } from "@/shared/lib/axios";
import { Button } from "@/shared/components/ui/button";

type Question = { id: string; title: string; prompt: string; language: "python" | "javascript" | "java" | "cpp" | "sql"; difficulty: string; starter_code: string };
type Submission = { id: string; question_title: string; overall_score: number; correctness_score: number; code_quality_score: number; feedback: string[] };

export function CodingPracticePage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selected, setSelected] = useState<Question | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { api.get<Question[]>("/coding/questions").then(({ data }) => { setQuestions(data); setSelected(data[0] ?? null); setCode(data[0]?.starter_code ?? ""); }).finally(() => setLoading(false)); }, []);
  const choose = (question: Question) => { setSelected(question); setCode(question.starter_code); setResult(null); };
  const submit = async () => { if (!selected || !code.trim()) return; setSubmitting(true); try { const { data } = await api.post<Submission>("/coding/submissions", { question_id: selected.id, language: selected.language, code }); setResult(data); } finally { setSubmitting(false); } };

  return <div className="space-y-6"><div className="glass-card p-6 rounded-2xl border border-border"><h2 className="text-2xl font-extrabold flex items-center gap-2"><Code2 className="text-fuchsia-400" />Coding Practice</h2><p className="text-xs text-foreground/70 mt-1">Practice curated questions and get safe static feedback on correctness cues and code quality.</p></div>{loading ? <Loader2 className="animate-spin text-fuchsia-400" /> : <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6"><aside className="glass-card p-4 rounded-2xl border border-border space-y-2">{questions.map((question) => <button key={question.id} onClick={() => choose(question)} className={`w-full text-left p-3 rounded-xl text-xs ${selected?.id === question.id ? "bg-fuchsia-600 text-white" : "bg-background hover:bg-accent"}`}><p className="font-bold">{question.title}</p><p className="mt-1 opacity-70 capitalize">{question.language} · {question.difficulty}</p></button>)}</aside><section className="glass-card p-6 rounded-2xl border border-border space-y-4">{selected && <><h3 className="font-extrabold">{selected.title}</h3><p className="text-sm text-foreground/80">{selected.prompt}</p><textarea value={code} onChange={(e) => setCode(e.target.value)} spellCheck={false} className="w-full min-h-72 rounded-xl bg-slate-950 text-emerald-300 p-4 font-mono text-sm border border-border" /><Button onClick={submit} disabled={submitting}>{submitting ? <Loader2 className="animate-spin" /> : <Send />}Submit for review</Button>{result && <div className="rounded-xl border border-emerald-500/30 p-4 bg-emerald-500/5"><p className="font-extrabold text-emerald-400">Overall score: {result.overall_score}%</p><p className="text-xs mt-1">Correctness cues: {result.correctness_score}% · Code quality: {result.code_quality_score}%</p>{result.feedback.map((feedback) => <p key={feedback} className="text-xs mt-2">• {feedback}</p>)}</div>}</>}</section></div>}</div>;
}
