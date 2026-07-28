/**
 * Resume Center API layer — HTTP calls for PDF resume upload and analysis.
 */

import { api } from "@/shared/lib/axios";
import type { Resume } from "../types";

/** POST /resumes/upload — Upload & Parse PDF Resume */
export async function uploadResume(file: File): Promise<Resume> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post<Resume>("/resumes/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

/** GET /resumes — List candidate's uploaded resumes */
export async function getResumes(): Promise<Resume[]> {
  const { data } = await api.get<Resume[]>("/resumes");
  return data;
}

/** GET /resumes/{id} — Get full ATS Resume Health Scorecard */
export async function getResumeById(resumeId: string): Promise<Resume> {
  const { data } = await api.get<Resume>(`/resumes/${resumeId}`);
  return data;
}

/** DELETE /resumes/{id} — Delete resume document */
export async function deleteResume(resumeId: string): Promise<void> {
  await api.delete(`/resumes/${resumeId}`);
}
