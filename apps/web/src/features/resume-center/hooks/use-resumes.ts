/**
 * Resume Center React Query hooks for file upload, listing, and analysis.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { type AxiosError } from "axios";

import { uploadResume, getResumes, getResumeById, deleteResume } from "../api/resumes-api";
import type { ApiErrorResponse } from "@/shared/types/api";

export function useResumesList() {
  return useQuery({
    queryKey: ["resumes"],
    queryFn: getResumes,
  });
}

export function useResumeDetails(resumeId: string) {
  return useQuery({
    queryKey: ["resumes", resumeId],
    queryFn: () => getResumeById(resumeId),
    enabled: !!resumeId,
  });
}

export function useUploadResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadResume(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.success(`Resume "${data.filename}" parsed successfully! ATS Score: ${data.ats_score}%`);
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const msg = error.response?.data?.detail ?? "Failed to process PDF resume.";
      toast.error(msg);
    },
  });
}

export function useDeleteResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (resumeId: string) => deleteResume(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.success("Resume removed from history.");
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const msg = error.response?.data?.detail ?? "Failed to delete resume.";
      toast.error(msg);
    },
  });
}
