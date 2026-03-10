import { useQuery } from "@tanstack/react-query";
import { getSessionFocusSamples, FocusSample } from "@/lib/api/focus-samples";

export function useSessionFocusSamples(sessionId?: string) {
  return useQuery<FocusSample[]>({
    queryKey: ["sessions", sessionId, "focusSamples"],
    queryFn: () => getSessionFocusSamples(sessionId!),
    enabled: !!sessionId,
    staleTime: 60_000,
  });
}
