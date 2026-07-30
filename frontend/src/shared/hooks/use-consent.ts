import { useCallback, useState } from "react";

export const CONSENT_POLICY_VERSION = "2026-07-29";
const STORAGE_KEY = "nipunhire.cookie-consent";

export type ConsentChoice = "all" | "essential" | "custom";

export interface ConsentPreferences {
  version: string;
  choice: ConsentChoice;
  analytics: boolean;
}

function readConsent(): ConsentPreferences | null {
  if (typeof window === "undefined") return null;
  try {
    const consent = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null") as ConsentPreferences | null;
    return consent?.version === CONSENT_POLICY_VERSION ? consent : null;
  } catch {
    return null;
  }
}

/** Versioned cookie-consent state. Gate non-essential integrations with `analytics`. */
export function useConsent() {
  const [consent, setConsent] = useState<ConsentPreferences | null>(readConsent);

  const saveConsent = useCallback((choice: ConsentChoice, analytics: boolean) => {
    const next = { version: CONSENT_POLICY_VERSION, choice, analytics };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    setConsent(next);
  }, []);

  return {
    consent,
    needsConsent: consent === null,
    analyticsAllowed: consent?.analytics === true,
    acceptAll: () => saveConsent("all", true),
    rejectNonEssential: () => saveConsent("essential", false),
    saveCustom: (analytics: boolean) => saveConsent("custom", analytics),
  };
}
