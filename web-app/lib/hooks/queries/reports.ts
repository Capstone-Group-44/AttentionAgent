import { useQuery } from "@tanstack/react-query";
import { getUserReports } from "@/lib/api/reports";
import type { Report } from "@/lib/api/reports";

export function useUserReports(userId?: string) {
  return useQuery<Report[]>({
    queryKey: ["reports", userId],
    queryFn: () => getUserReports(userId!),
    enabled: !!userId,
    staleTime: 60_000,
  });
}
