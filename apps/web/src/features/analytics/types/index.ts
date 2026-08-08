/**
 * Analytics & Job Applications feature types & status enums.
 */

export type ApplicationStatus =
  | "saved"
  | "applied"
  | "shortlisted"
  | "interview_scheduled"
  | "offer_received"
  | "rejected";

export interface TimelineEvent {
  status: ApplicationStatus;
  timestamp: string;
  note?: string;
}

export interface ApplicationResponse {
  id: string;
  candidate_id: string;
  job_id: string;
  resume_id?: string;
  status: ApplicationStatus;
  notes?: string;
  timeline: TimelineEvent[];
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  job_id: string;
  resume_id?: string;
  notes?: string;
}

export interface ApplicationStatusUpdate {
  status: ApplicationStatus;
  note?: string;
}

export interface AnalyticsMetrics {
  total_applications: number;
  shortlisted_count: number;
  interview_count: number;
  offer_count: number;
  conversion_rate: number;
}
