import { useEffect, useState } from "react";
import { Bot, Loader2, Send } from "lucide-react";
import { api } from "@/shared/lib/axios";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";

type CoachMessage = { id: string; question: string; answer: string; created_at: string };

export function CareerCoachPage() {
  const [messages, setMessages] = useState<CoachMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  useEffect(() => { api.get<CoachMessage[]>("/career-coach/history").then(({ data }) => setMessages(data.reverse())); }, []);
  const ask = async (event: React.FormEvent) => { event.preventDefault(); if (!question.trim()) return; setLoading(true); try { const { data } = await api.post<CoachMessage>("/career-coach/ask", { question }); setMessages((current) => [...current, data]); setQuestion(""); } finally { setLoading(false); } };
  return <div className="max-w-4xl mx-auto space-y-6"><div className="glass-card p-6 rounded-2xl border border-border"><h2 className="text-2xl font-extrabold flex items-center gap-2"><Bot className="text-fuchsia-400" />AI Career Coach</h2><p className="text-xs text-foreground/70 mt-1">Ask for help with resumes, skills, interview preparation, or your career roadmap.</p></div><div className="glass-card rounded-2xl border border-border p-6 space-y-4 min-h-80">{messages.length === 0 && <p className="text-sm text-foreground/70">Try: “How should I improve my FastAPI resume project?”</p>}{messages.map((message) => <div key={message.id} className="space-y-2"><p className="ml-auto max-w-[80%] rounded-xl bg-fuchsia-600 text-white p-3 text-sm">{message.question}</p><p className="max-w-[85%] rounded-xl bg-background border border-border p-3 text-sm">{message.answer}</p></div>)}</div><form onSubmit={ask} className="flex gap-2"><Input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask your career coach..." /><Button type="submit" disabled={loading}>{loading ? <Loader2 className="animate-spin" /> : <Send />}</Button></form></div>;
}
