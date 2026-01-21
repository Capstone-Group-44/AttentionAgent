import { useQuery } from "@tanstack/react-query";
import { getUserSessionRows, type SessionRow } from "@/lib/api/sessions";

export function useUserSessionRows(userId?: string) {
  return useQuery<SessionRow[]>({
    queryKey: ["sessionRows", userId],
    queryFn: () => getUserSessionRows(userId!),
    enabled: !!userId,
    staleTime: 60_000,
  });
}
