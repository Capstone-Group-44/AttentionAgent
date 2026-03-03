'use client'

import { use } from 'react'
import { useAuthUser } from '@/lib/hooks/use-auth-user'
import { formatDuration, formatSessionDateTime, focusScoreToPercent } from '@/lib/utils'
import { StatCard } from '@/components/stat-card'
import { Clock, Hourglass, Timer, TrendingUp } from 'lucide-react'
import { useRouter } from "next/navigation";
import { useUserReports } from "@/lib/hooks/queries/reports";
import { useUserSessionRows } from "@/lib/hooks/queries/session-rows";
import { AuthRequired } from '@/app/_components/auth-required'
import { useSessionFocusSamples } from "@/lib/hooks/queries/focus-samples";
import { FocusTrendChart } from "../_components/focus-trend-chart";
export default function Page({
  params,
}: {
  params: Promise<{ sessionId: string }>
}) {
  const router = useRouter();
  const { sessionId } = use(params)
  const { user, authReady } = useAuthUser()
  
  const sessionRowsQ = useUserSessionRows(user?.uid)
  const reportsQ = useUserReports(user?.uid)
  const focusSamplesQ = useSessionFocusSamples(sessionId);
  const focusSamples = focusSamplesQ.data ?? [];

  const sessionRows = sessionRowsQ.data ?? []
  const reports = reportsQ.data ?? []

  const session = sessionRows.find(s => s.id === sessionId) ?? null
  const report = reports.find(r => r.sessionId === sessionId) ?? null

  if (!authReady) return null;
  if (!user) return <AuthRequired message="Log in to view your session history." />;
  if (sessionRowsQ.isLoading || reportsQ.isLoading) {
      return <div className="p-6">Loading session…</div>
    }

if (focusSamplesQ.error)
  console.log("focusSamples error", focusSamplesQ.error);

  return (
    <div className="space-y-6">

      <div>
        <h1 className="text-xl font-semibold">Session Details</h1>
        {session && (
    <p className="text-sm text-muted-foreground">
      {formatSessionDateTime(session.startTime)}
    </p>
  )}
      </div>


<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  <StatCard
    label="Session Duration"
    value={session ? formatDuration(session.durationSeconds) : "—"}
    icon={Clock}
  />
  <StatCard
    label="Total Focus Time"
    value={report ? formatDuration(report.totalFocusTime) : "—"}
    icon={Hourglass}
  />
  <StatCard
    label="Focus Score"
    value={report ? `${focusScoreToPercent(report.avgFocusScore)}/100` : "—"}
    icon={TrendingUp}
  />
</div>

  <div className="rounded-xl border p-4">
  <div className="mb-2 text-xl font-medium">Focus Trend</div>
  <div className="text-sm text-muted-foreground pb-4"> 
    Focus score over time during this session.
  </div>

  {focusSamplesQ.isLoading && (
    <div className="text-sm text-muted-foreground">
      Loading focus trend…
    </div>
  )}
  

  {focusSamplesQ.error && (
    <div className="text-sm text-red-500">
      Failed to load focus samples.
    </div>
  )}

  {!focusSamplesQ.isLoading &&
    !focusSamplesQ.error &&
    focusSamples.length >= 2 &&
    session && (
      <FocusTrendChart
        samples={focusSamples}
        sessionStart={session.startTime}
      />
    )}
</div>

  </div>
  )
}