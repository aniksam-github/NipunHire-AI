/**
 * Jobs React Query hooks for queries & mutations.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { type AxiosError } from "axios";

import { getJobs, getJobById, createJob, deleteJob } from "../api/jobs-api";
import type { JobCreatePayload } from "../types";
import type { ApiErrorResponse } from "@/shared/types/api";

export function useJobsList(params?: { recruiter_only?: boolean; is_active?: boolean }) {
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => getJobs(params),
  });
}

export function useJobDetails(jobId: string) {
  return useQuery({
    queryKey: ["jobs", jobId],
    queryFn: () => getJobById(jobId),
    enabled: !!jobId,
  });
}

export function useCreateJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: JobCreatePayload) => createJob(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      toast.success(`Job position "${data.title}" posted successfully!`);
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const msg = error.response?.data?.detail ?? "Failed to create job posting.";
      toast.error(msg);
    },
  });
}

export function useDeleteJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => deleteJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      toast.success("Job posting removed.");
    },
    onError: (error: AxiosError<ApiErrorResponse>) => {
      const msg = error.response?.data?.detail ?? "Failed to delete job posting.";
      toast.error(msg);
    },
  });
}
