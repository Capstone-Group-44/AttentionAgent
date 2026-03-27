import { useQuery } from "@tanstack/react-query";
import { getUserProfile } from "@/lib/api/profile";

export function useUserProfile(uid?: string) {
  return useQuery({
    queryKey: ["profile", uid],
    queryFn: () => getUserProfile(uid!),
    enabled: !!uid,
  });
}
