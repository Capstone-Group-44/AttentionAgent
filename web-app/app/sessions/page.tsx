"use client";
import { StatCard } from "@/components/stat-card";
import { calcAvgFocusScore, calcTotalFocusTime, formatDuration } from "@/lib/utils";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { Clock, Layers, TrendingUp } from "lucide-react";
import { useRouter } from "next/navigation";
import { useUserReports } from "@/lib/hooks/queries/reports";
import { useUserSessionRows } from "@/lib/hooks/queries/session-rows";
import { SessionHistoryTable } from "./_components/session-history-table";
import { useState } from "react";

type FilteredSummary = {
  totalSessions: number;
  avgFocusScore: number | null;
};

export default function SessionsPage(){
  const router = useRouter();

  const { user, authReady } = useAuthUser()
  const userId = user?.uid

  const sessionRowsQ = useUserSessionRows(userId)
  const reportsQ = useUserReports(userId)

  // Safe defaults while data loads
  const sessionRows = sessionRowsQ.data ?? []
  const reports = reportsQ.data ?? []

  const sessionCount = sessionRows.length
  const totalFocus = calcTotalFocusTime(reports)
  const avgFocus = calcAvgFocusScore(reports)

  const [filteredSummary, setFilteredSummary] = useState<FilteredSummary | null>(null);



// some error handling

if (!authReady) return <div className="p-6">Loading auth…</div>
if (!user) return <div className="p-6 text-red-500">Please log in.</div>
if (sessionRowsQ.isLoading || reportsQ.isLoading) return <div className="p-6">Loading…</div>
if (sessionRowsQ.error || reportsQ.error) return <div className="p-6 text-red-500">Failed to load data.</div>


return (
    <div className="space-y-6">

      <h1 className="text-xl font-semibold">Overall Progress</h1>

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

      {/* show filtered summary only when filters are active */}
      {filteredSummary && (
        <div className="text-sm text-muted-foreground">
          Filtered: {filteredSummary.totalSessions} sessions •{" "}
          {filteredSummary.avgFocusScore === null ? "—" : `${filteredSummary.avgFocusScore}/100`} avg
        </div>
      )}

      {/* Session History Table */}

      <h1 className="text-xl font-semibold">Session History</h1>

      <SessionHistoryTable
        sessionRows={sessionRows}
        onRowClick={(sessionId) => {
          router.push(`/sessions/${sessionId}`)
        }}
        onFilteredSummaryChange={setFilteredSummary}
      />
    </div>
  )}