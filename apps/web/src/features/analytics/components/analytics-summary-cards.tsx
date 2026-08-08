/**
 * AnalyticsSummaryCards — KPI summary metric scorecards for candidate pipeline analytics.
 */

import { Users, UserCheck, CalendarCheck, Award } from "lucide-react";
import { ScoreCard } from "@/shared/design-system";
import type { ApplicationResponse } from "../types";

interface AnalyticsSummaryCardsProps {
  applications: ApplicationResponse[];
}

export function AnalyticsSummaryCards({ applications }: AnalyticsSummaryCardsProps) {
  const total = applications.length;
  const shortlisted = applications.filter(
    (a) => a.status === "shortlisted" || a.status === "interview_scheduled" || a.status === "offer_received"
  ).length;
  const interviewing = applications.filter((a) => a.status === "interview_scheduled").length;
  const offered = applications.filter((a) => a.status === "offer_received").length;

  const shortlistRate = total > 0 ? ((shortlisted / total) * 100).toFixed(1) : "0.0";
  const offerRate = total > 0 ? ((offered / total) * 100).toFixed(1) : "0.0";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <ScoreCard
        title="Pipeline Volume"
        value={total.toString()}
        description="Total candidates in pipeline"
        icon={<Users className="size-5 text-fuchsia-400" />}
        trend="Active Applications"
      />

      <ScoreCard
        title="Shortlist Rate"
        value={`${shortlistRate}%`}
        description={`${shortlisted} candidates qualified`}
        icon={<UserCheck className="size-5 text-emerald-400" />}
        trend="High compatibility"
      />

      <ScoreCard
        title="Interviews Scheduled"
        value={interviewing.toString()}
        description="Active screening interviews"
        icon={<CalendarCheck className="size-5 text-purple-400" />}
        trend="In-progress"
      />

      <ScoreCard
        title="Offer Rate"
        value={`${offerRate}%`}
        description={`${offered} placement offers extended`}
        icon={<Award className="size-5 text-amber-400" />}
        trend="Top match quality"
      />
    </div>
  );
}
