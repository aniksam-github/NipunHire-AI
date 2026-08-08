import { useQuery } from "@tanstack/react-query";
import { getCandidateDashboard } from "../api/dashboard-api";

export const useCandidateDashboard = () => useQuery({
  queryKey: ["candidate-dashboard"],
  queryFn: getCandidateDashboard,
});
