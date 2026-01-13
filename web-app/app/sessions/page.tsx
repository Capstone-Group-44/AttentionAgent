"use client";
import { StatCard } from "@/components/stat-card";
import { SessionHistoryList } from "./_components/session-history-list";
import { calcAvgFocusScore, calcTotalFocusTime, formatDuration } from "@/lib/utils";
import { getUserReports } from "@/lib/api/reports";
import { getUserSessions } from "@/lib/api/sessions";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { Clock, Layers, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";

export default function SessionsPage(){
    const { user, authReady } = useAuthUser()

  const [totalFocus, setTotalFocus] = useState(0)
  const [avgFocus, setAvgFocus] = useState<number | null>(null)
  const [sessionCount, setSessionCount] = useState(0)

  useEffect(() => {
    if (!authReady || !user) return

    const userId = user.uid
    async function loadStats() {
      const [sessions, reports] = await Promise.all([
        getUserSessions(userId),
        getUserReports(userId),
      ])

      setSessionCount(sessions.length)

      const total = calcTotalFocusTime(reports);
      setTotalFocus(total)

      setAvgFocus(calcAvgFocusScore(reports))
    }

    loadStats()
  }, [authReady, user])
return (
    <div className="space-y-6">

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total Focus Time"
          value={formatDuration(totalFocus)}
          icon={Clock}
        />
        <StatCard
          label="Total Sessions"
          value={sessionCount}
          icon={Layers}
        />
        <StatCard
          label="Avg Focus Score"
          value={avgFocus === null ? "—" : `${avgFocus}/100`}
          icon={TrendingUp}
        />
      </div>

      <SessionHistoryList />
    </div>
  )}