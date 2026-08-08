/**
 * Analytics & Applications API layer — HTTP calls for application pipeline tracking.
 */

import { api } from "@/shared/lib/axios";
import type {
  ApplicationResponse,
  ApplicationCreate,
  ApplicationStatusUpdate,
} from "../types";

/** GET /applications — List candidate applications */
export async function getApplications(): Promise<ApplicationResponse[]> {
  const { data } = await api.get<ApplicationResponse[]>("/applications");
  return data;
}

/** POST /applications — Submit a job application */
export async function createApplication(
  payload: ApplicationCreate
): Promise<ApplicationResponse> {
  const { data } = await api.post<ApplicationResponse>("/applications", payload);
  return data;
}

/** PATCH /applications/{id}/status — Update pipeline stage */
export async function updateApplicationStatus(
  applicationId: string,
  payload: ApplicationStatusUpdate
): Promise<ApplicationResponse> {
  const { data } = await api.patch<ApplicationResponse>(
    `/applications/${applicationId}/status`,
    payload
  );
  return data;
}
