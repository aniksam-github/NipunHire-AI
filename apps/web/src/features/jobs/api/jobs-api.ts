/**
 * Jobs API layer — HTTP calls for job CRUD operations.
 */

import { api } from "@/shared/lib/axios";
import type { Job, JobCreatePayload } from "../types";

/** GET /jobs — List job postings */
export async function getJobs(params?: { recruiter_only?: boolean; is_active?: boolean }): Promise<Job[]> {
  const { data } = await api.get<Job[]>("/jobs", { params });
  return data;
}

/** GET /jobs/{id} — Get job details */
export async function getJobById(jobId: string): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${jobId}`);
  return data;
}

/** POST /jobs — Create a job posting */
export async function createJob(payload: JobCreatePayload): Promise<Job> {
  const { data } = await api.post<Job>("/jobs", payload);
  return data;
}

/** PATCH /jobs/{id} — Update job posting */
export async function updateJob(jobId: string, payload: Partial<JobCreatePayload>): Promise<Job> {
  const { data } = await api.patch<Job>(`/jobs/${jobId}`, payload);
  return data;
}

/** DELETE /jobs/{id} — Delete job posting */
export async function deleteJob(jobId: string): Promise<void> {
  await api.delete(`/jobs/${jobId}`);
}
