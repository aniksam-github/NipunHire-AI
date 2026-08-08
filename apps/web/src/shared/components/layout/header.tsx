/**
 * Header — topbar header for dashboard shell with breadcrumb & search.
 */

import { Search, Bell } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/shared/lib/axios";
import { Input } from "@/shared/components/ui/input";
import { useAuthStore } from "@/features/auth/stores/auth-store";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title = "Recruiter Overview", subtitle }: HeaderProps) {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);
  useEffect(() => { api.get<{ unread_count: number }>("/notifications/unread-count").then(({ data }) => setUnread(data.unread_count)).catch(() => setUnread(0)); }, []);

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-card/80 backdrop-blur-md border-b border-border shadow-xs">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
          <span>{title}</span>
        </h1>
        {subtitle && (
          <p className="text-xs font-semibold text-foreground/80">{subtitle}</p>
        )}
      </div>

      {/* Right Controls: Search, Notifications, Quick Actions */}
      <div className="flex items-center gap-4">
        {/* Search Bar */}
        <div className="relative w-64 hidden sm:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-fuchsia-400" />
          <Input
            type="text"
            placeholder="Search candidates, jobs..."
            className="pl-9 h-9 bg-background border-border text-foreground text-xs font-medium placeholder:text-muted-foreground/90 rounded-xl"
          />
        </div>

        {/* Notifications Icon */}
        <button onClick={() => navigate("/notifications")} className="relative p-2 rounded-xl border border-border bg-background hover:bg-accent text-foreground/80 transition-colors">
          <Bell className="size-4 text-fuchsia-400" />
          {unread > 0 && <span className="absolute -top-1 -right-1 min-w-4 h-4 px-1 rounded-full bg-fuchsia-500 text-[9px] text-white font-bold flex items-center justify-center">{unread}</span>}
        </button>

        {/* Quick User Pill */}
        <div className="flex items-center gap-2 pl-2 border-l border-border">
          <div className="size-8 rounded-full bg-fuchsia-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
            {user?.full_name?.charAt(0) ?? "U"}
          </div>
          <div className="hidden lg:block text-xs text-left">
            <p className="font-bold text-foreground leading-tight">{user?.full_name ?? "User"}</p>
            <p className="text-[10px] font-semibold text-fuchsia-400 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
