"use client";

import { useMemo } from "react";
import { useUserSessions } from "@/lib/hooks/queries/sessions";
import { useUserReports } from "@/lib/hooks/queries/reports";
import { calcTodayProgress } from "@/lib/utils";

export function useTodayProgress(userId?: string) {
  const sessionsQ = useUserSessions(userId);
  const reportsQ = useUserReports(userId);

  const stats = useMemo(
    () => calcTodayProgress(sessionsQ.data ?? [], reportsQ.data ?? []),
    [sessionsQ.data, reportsQ.data]
  );

  return {
    stats,
    loading: sessionsQ.isLoading || reportsQ.isLoading,
    error: sessionsQ.error ?? reportsQ.error,
  };
}
