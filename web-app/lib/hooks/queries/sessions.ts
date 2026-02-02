import { useQuery } from "@tanstack/react-query";
import { getUserSessions } from "@/lib/api/sessions";
import type { Session } from "@/lib/api/sessions";

export function useUserSessions(userId?: string) {
  return useQuery<Session[]>({
    queryKey: ["sessions", userId],
    queryFn: () => getUserSessions(userId!),
    enabled: !!userId,
    staleTime: 60_000, // 1 min
  });
}
