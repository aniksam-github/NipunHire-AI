/**
 * Settings React Query hooks for fetching & updating user profile state.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { type AxiosError } from "axios";

import { getProfile, updateProfile } from "../api/settings-api";
import type { ProfileResponse, ProfileUpdate } from "../types";
import type { ApiErrorResponse } from "@/shared/types/api";

export function useProfile() {
  return useQuery<ProfileResponse>({
    queryKey: ["profile", "me"],
    queryFn: getProfile,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation<ProfileResponse, AxiosError<ApiErrorResponse>, ProfileUpdate>({
    mutationFn: updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      toast.success("Profile settings updated successfully!");
    },
    onError: (error) => {
      const msg = error.response?.data?.detail ?? "Failed to update profile settings.";
      toast.error(msg);
    },
  });
}
