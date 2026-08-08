/**
 * SettingsPage — main page for user account details & candidate profile settings.
 */

import { Settings, Shield, User, Sparkles, Loader2, Save } from "lucide-react";
import { useState } from "react";
import { api } from "@/shared/lib/axios";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { ConfidenceMeter } from "@/shared/design-system";
import { ProfileForm } from "./profile-form";
import { useProfile } from "../hooks/use-settings";
import { useAuthStore } from "@/features/auth/stores/auth-store";

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const { data: profile, isLoading } = useProfile();

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-border shadow-xl">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold tracking-tight text-foreground flex items-center gap-2">
            <span>Account & Profile Settings</span>
            <Settings className="size-5 text-fuchsia-400" />
          </h2>
          <p className="text-xs font-semibold text-foreground/80">
            Manage candidate profile details, technical skill stack, and application preferences.
          </p>
        </div>
      </div>

      {/* Account Info Bar */}
      <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
        <div className="flex items-center gap-4">
          <div className="size-14 rounded-2xl bg-fuchsia-600/20 text-fuchsia-400 border border-fuchsia-500/30 flex items-center justify-center font-extrabold text-xl shadow-md">
            {user?.full_name?.charAt(0) ?? "U"}
          </div>
          <div>
            <h3 className="text-lg font-extrabold text-foreground flex items-center gap-2">
              <span>{user?.full_name ?? "User"}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-fuchsia-500/20 text-fuchsia-300 uppercase tracking-wider">
                {user?.role}
              </span>
            </h3>
            <p className="text-xs font-semibold text-foreground/80 flex items-center gap-3 pt-0.5">
              <span className="flex items-center gap-1">
                <User className="size-3.5 text-fuchsia-400" />
                {user?.email}
              </span>
              <span className="flex items-center gap-1 text-emerald-400">
                <Shield className="size-3.5" />
                Authenticated Session
              </span>
            </p>
          </div>
        </div>

        {profile && (
          <div className="pt-2">
            <ConfidenceMeter
              score={profile.completion_percentage}
              label="Profile Completion Score"
            />
          </div>
        )}
      </div>

      {/* Profile Form Card */}
      <div className="glass-card p-6 rounded-2xl border border-border space-y-5">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <h3 className="text-lg font-extrabold text-foreground flex items-center gap-2">
            <span>Candidate Profile Details</span>
            <Sparkles className="size-4 text-fuchsia-400" />
          </h3>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center p-8 space-y-3">
            <Loader2 className="animate-spin size-7 text-fuchsia-400" />
            <p className="text-xs font-bold text-foreground">Loading profile data...</p>
          </div>
        ) : profile ? (
          <ProfileForm profile={profile} />
        ) : (
          <p className="text-xs text-destructive font-bold">Failed to load profile details.</p>
        )}
      </div>
      <AccountPreferences />
    </div>
  );
}

function AccountPreferences() {
  const [theme, setTheme] = useState("system");
  const [notifications, setNotifications] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const savePreferences = async () => {
    await api.patch("/settings/me", { theme, notifications_enabled: notifications, email_notifications_enabled: emailNotifications });
    document.documentElement.classList.toggle("dark", theme === "dark");
  };
  const changePassword = async (event: React.FormEvent) => { event.preventDefault(); await api.post("/auth/change-password", { current_password: currentPassword, new_password: newPassword }); setCurrentPassword(""); setNewPassword(""); };
  return <div className="glass-card p-6 rounded-2xl border border-border space-y-5"><h3 className="text-lg font-extrabold">Preferences & Security</h3><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><label className="text-xs font-bold">Theme<select value={theme} onChange={(e) => setTheme(e.target.value)} className="mt-2 w-full h-10 rounded-xl border border-border bg-background px-3"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label><label className="flex gap-2 items-center text-sm font-semibold pt-5"><input type="checkbox" checked={notifications} onChange={(e) => setNotifications(e.target.checked)} />In-app notifications</label><label className="flex gap-2 items-center text-sm font-semibold pt-5"><input type="checkbox" checked={emailNotifications} onChange={(e) => setEmailNotifications(e.target.checked)} />Email notifications</label></div><Button onClick={savePreferences}><Save />Save preferences</Button><form onSubmit={changePassword} className="border-t border-border pt-5 space-y-3"><h4 className="font-extrabold text-sm">Change password</h4><div className="grid grid-cols-1 md:grid-cols-2 gap-3"><Input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder="Current password" /><Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New password (8+ characters)" /></div><Button type="submit" variant="outline">Update password</Button></form></div>;
}
