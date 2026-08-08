import { useState } from "react";
import { Award, BrainCircuit, CheckCircle2, Loader2, Target, Trophy } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { useCareerActions, useCareerProgress, useGoals, useInterviews } from "../hooks/use-career-growth";
import type { InterviewSession, InterviewType } from "../types";

export function CareerGrowthPage() {
  const [goalTitle, setGoalTitle] = useState("");
  const [topic, setTopic] = useState("Python");
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [answers, setAnswers] = useState("");
  const { data: progress, isLoading } = useCareerProgress();
  const { data: goals = [] } = useGoals();
  const { data: interviews = [] } = useInterviews();
  const actions = useCareerActions();

  const createGoal = (event: React.FormEvent) => {
    event.preventDefault();
    if (!goalTitle.trim()) return;
    actions.createGoal.mutate({ title: goalTitle, category: "career", target_value: 1, unit: "milestone" }, { onSuccess: () => setGoalTitle("") });
  };
  const beginInterview = () => actions.startInterview.mutate(
    { interview_type: "technical" as InterviewType, topic, question_count: 3 },
    { onSuccess: setSession }
  );
  const finishInterview = () => {
    if (!session || !answers.trim()) return;
    actions.submitInterview.mutate({ id: session.id, answers: answers.split("\n").filter(Boolean) }, { onSuccess: setSession });
  };

  return <div className="space-y-6">
    <div className="glass-card p-6 rounded-2xl border border-border shadow-xl">
      <h2 className="text-2xl font-extrabold text-foreground flex items-center gap-2"><BrainCircuit className="size-6 text-fuchsia-400" />Career Growth Studio</h2>
      <p className="text-xs font-semibold text-foreground/70 mt-1">Practice interviews, set career goals, and track measurable progress.</p>
    </div>

    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <Metric label="Active goals" value={progress?.active_goals ?? 0} icon={<Target />} />
      <Metric label="Goals achieved" value={progress?.completed_goals ?? 0} icon={<Trophy />} />
      <Metric label="Mock interviews" value={progress?.completed_interviews ?? 0} icon={<BrainCircuit />} />
      <Metric label="Interview average" value={progress?.interview_average_score ? `${progress.interview_average_score}%` : "—"} icon={<Award />} />
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h3 className="font-extrabold text-foreground">Goal Planner</h3>
        <form onSubmit={createGoal} className="flex gap-2"><Input value={goalTitle} onChange={(e) => setGoalTitle(e.target.value)} placeholder="e.g. Complete FastAPI course" /><Button type="submit" disabled={actions.createGoal.isPending}>Add goal</Button></form>
        <div className="space-y-2">
          {goals.length === 0 ? <p className="text-xs text-foreground/70">Set your first goal to start building momentum.</p> : goals.map((goal) => <div key={goal.id} className="flex items-center justify-between gap-3 p-3 rounded-xl bg-background border border-border"><div><p className="text-sm font-bold">{goal.title}</p><p className="text-[11px] text-foreground/70">{goal.current_value}/{goal.target_value} {goal.unit}</p></div><Button size="sm" variant="outline" disabled={goal.status === "completed"} onClick={() => actions.updateGoal.mutate({ goal, value: goal.current_value + 1 })}>{goal.status === "completed" ? "Done" : "Progress"}</Button></div>)}
        </div>
      </section>

      <section className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <h3 className="font-extrabold text-foreground">AI Interview Practice</h3>
        <div className="flex gap-2"><Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic, e.g. SQL" /><Button onClick={beginInterview} disabled={actions.startInterview.isPending}>{actions.startInterview.isPending ? <Loader2 className="animate-spin" /> : "Start practice"}</Button></div>
        {session ? <div className="space-y-3 p-4 rounded-xl bg-background border border-fuchsia-500/30"><p className="text-xs font-bold text-fuchsia-400">{session.topic} practice session</p>{session.questions.map((question, index) => <p key={question} className="text-sm"><span className="font-bold">{index + 1}.</span> {question}</p>)}{session.overall_score === null ? <><textarea value={answers} onChange={(e) => setAnswers(e.target.value)} placeholder="Write one answer per line..." className="w-full min-h-24 rounded-xl border border-border bg-card p-3 text-sm" /><Button onClick={finishInterview} disabled={actions.submitInterview.isPending}>Get feedback</Button></> : <div className="space-y-2"><p className="font-extrabold text-emerald-400">Score: {session.overall_score}%</p>{session.feedback.map((item) => <p key={item} className="text-xs text-foreground/80">• {item}</p>)}</div>}</div> : <p className="text-xs text-foreground/70">Choose a topic to generate a three-question mock interview.</p>}
      </section>
    </div>

    <section className="glass-card p-6 rounded-2xl border border-border"><h3 className="font-extrabold text-foreground mb-3">Achievements & Interview History</h3><div className="flex flex-wrap gap-2 mb-4">{progress?.achievements.length ? progress.achievements.map((achievement) => <span key={achievement} className="text-xs px-3 py-1 rounded-full bg-amber-500/15 text-amber-300"><CheckCircle2 className="inline size-3 mr-1" />{achievement}</span>) : <span className="text-xs text-foreground/70">Complete an interview or goal to unlock an achievement.</span>}</div>{interviews.slice(0, 3).map((interview) => <div key={interview.id} className="text-xs py-2 border-t border-border/60 flex justify-between"><span>{interview.topic} · {interview.interview_type}</span><span>{interview.overall_score === null ? "In progress" : `${interview.overall_score}%`}</span></div>)}</section>
    {isLoading && <p className="text-xs text-foreground/70">Loading your career data…</p>}
  </div>;
}

function Metric({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return <div className="glass-card p-4 rounded-2xl border border-border"><div className="text-fuchsia-400 mb-2">{icon}</div><p className="text-xl font-extrabold">{value}</p><p className="text-[11px] font-semibold text-foreground/70">{label}</p></div>;
}
