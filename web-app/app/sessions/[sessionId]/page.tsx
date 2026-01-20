'use client'

import { use } from 'react'
import { useAuthUser } from '@/lib/hooks/use-auth-user'
import { formatDuration, formatSessionDateTime, focusScoreToPercent } from '@/lib/utils'
import { StatCard } from '@/components/stat-card'
import { Clock, Hourglass, Timer, TrendingUp } from 'lucide-react'
import { useRouter } from "next/navigation";
import { useUserReports } from "@/lib/hooks/queries/reports";
import { useUserSessionRows } from "@/lib/hooks/queries/session-rows";


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

  const sessionRows = sessionRowsQ.data ?? []
  const reports = reportsQ.data ?? []

  const session = sessionRows.find(s => s.id === sessionId) ?? null
  const report = reports.find(r => r.sessionId === sessionId) ?? null


  if (!authReady) return <div className="p-6">Loading auth…</div>
  if (sessionRowsQ.isLoading || reportsQ.isLoading) {
      return <div className="p-6">Loading session…</div>
    }
  if (!user) return <div className="p-6 text-red-500">Please log in.</div>

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
    </div>
  )
}