/**
 * Analytics React Query hooks for application pipeline tracking & state mutations.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { type AxiosError } from "axios";

import {
  getApplications,
  createApplication,
  updateApplicationStatus,
} from "../api/analytics-api";
import type {
  ApplicationResponse,
  ApplicationCreate,
  ApplicationStatusUpdate,
} from "../types";
import type { ApiErrorResponse } from "@/shared/types/api";

export function useApplicationsList() {
  return useQuery<ApplicationResponse[]>({
    queryKey: ["applications"],
    queryFn: getApplications,
  });
}

export function useCreateApplication() {
  const queryClient = useQueryClient();

  return useMutation<ApplicationResponse, AxiosError<ApiErrorResponse>, ApplicationCreate>({
    mutationFn: createApplication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      toast.success("Application submitted successfully!");
    },
    onError: (error) => {
      const msg = error.response?.data?.detail ?? "Failed to submit job application.";
      toast.error(msg);
    },
  });
}

export function useUpdateApplicationStatus() {
  const queryClient = useQueryClient();

  return useMutation<
    ApplicationResponse,
    AxiosError<ApiErrorResponse>,
    { id: string; payload: ApplicationStatusUpdate }
  >({
    mutationFn: ({ id, payload }) => updateApplicationStatus(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      toast.success(`Application status updated to "${data.status.replace("_", " ")}"`);
    },
    onError: (error) => {
      const msg = error.response?.data?.detail ?? "Failed to update status.";
      toast.error(msg);
    },
  });
}
