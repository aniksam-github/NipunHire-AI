import { useEffect, useState } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { api } from "@/shared/lib/axios";
import { Button } from "@/shared/components/ui/button";

type Notification = { id: string; title: string; message: string; type: string; is_read: boolean; created_at: string };

export function NotificationCenterPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const load = () => api.get<Notification[]>("/notifications").then(({ data }) => setItems(data));
  useEffect(() => { void load(); }, []);
  const markAll = async () => { await api.post("/notifications/read-all"); await load(); };
  const markRead = async (id: string) => { await api.patch(`/notifications/${id}/read`); await load(); };
  return <div className="max-w-4xl mx-auto space-y-6"><div className="flex items-center justify-between glass-card p-6 rounded-2xl border border-border"><div><h2 className="text-2xl font-extrabold flex gap-2 items-center"><Bell className="text-fuchsia-400" />Notifications</h2><p className="text-xs text-foreground/70 mt-1">Updates about your resume, applications, interviews, and reports.</p></div><Button variant="outline" onClick={markAll}><CheckCheck />Mark all read</Button></div><div className="space-y-3">{items.length === 0 ? <p className="glass-card p-8 rounded-2xl border border-border text-center text-sm text-foreground/70">You are all caught up.</p> : items.map((item) => <button key={item.id} onClick={() => !item.is_read && markRead(item.id)} className={`w-full text-left glass-card p-4 rounded-2xl border ${item.is_read ? "border-border opacity-70" : "border-fuchsia-500/40"}`}><div className="flex justify-between gap-4"><p className="font-bold text-sm">{item.title}</p>{!item.is_read && <span className="size-2 rounded-full bg-fuchsia-500 mt-1.5" />}</div><p className="text-xs text-foreground/70 mt-1">{item.message}</p><p className="text-[10px] text-foreground/50 mt-2">{new Date(item.created_at).toLocaleString()}</p></button>)}</div></div>;
}
