import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/shared/components/ui/button";
import { useConsent } from "@/shared/hooks/use-consent";

/** Global consent control. Non-essential scripts must check `analyticsAllowed` before loading. */
export function ConsentBanner() {
  const { needsConsent, acceptAll, rejectNonEssential, saveCustom } = useConsent();
  const [customizing, setCustomizing] = useState(false);
  const [analytics, setAnalytics] = useState(false);

  if (!needsConsent) return null;

  return (
    <section
      className="fixed inset-x-4 bottom-4 z-50 mx-auto max-w-3xl rounded-2xl border border-border bg-card p-5 shadow-2xl"
      aria-label="Cookie consent"
    >
      <h2 className="text-base font-bold text-foreground">Your privacy choices</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Essential storage keeps the app working. Optional analytics stays disabled until you allow it. Read our{" "}
        <Link className="font-semibold text-fuchsia-500 underline" to="/cookie-policy" target="_blank" rel="noreferrer">Cookie Policy</Link>.
      </p>

      {customizing && (
        <label className="mt-4 flex items-center gap-2 text-sm text-foreground">
          <input type="checkbox" checked={analytics} onChange={(event) => setAnalytics(event.target.checked)} />
          Allow optional analytics
        </label>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={acceptAll}>Accept All</Button>
        <Button variant="outline" onClick={rejectNonEssential}>Reject Non-Essential</Button>
        {customizing ? (
          <Button variant="outline" onClick={() => saveCustom(analytics)}>Save choices</Button>
        ) : (
          <Button variant="ghost" onClick={() => setCustomizing(true)}>Customize</Button>
        )}
      </div>
    </section>
  );
}
