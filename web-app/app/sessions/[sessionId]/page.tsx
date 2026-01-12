'use client'

import { use } from 'react'
import { useEffect, useState } from 'react'
import { getSession, type Session } from '@/lib/api/sessions'
import { getReport, type Report } from '@/lib/api/reports'
import { useAuthUser } from '@/lib/hooks/use-auth-user'
import { auth } from '@/lib/firebase'
import { formatDuration, formatSessionDateTime, focusScoreToPercent } from '@/lib/utils'
import { StatCard } from '@/components/stat-card'

export default function Page({
  params,
}: {
  params: Promise<{ sessionId: string }>
}) {
  const { sessionId } = use(params)
  const { user, authReady } = useAuthUser()

  const [session, setSession] = useState<Session | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setError(null)
      setLoading(true)

      if (!authReady) return

      if (!user) {
        setError('Please log in to view this session.')
        setLoading(false)
        return
      }
      console.log('authReady:', authReady)
console.log('user uid:', user?.uid)
console.log('sessionId:', sessionId)

      try {
        const sessionData = await getSession(sessionId)
        if (cancelled) return

        setSession(sessionData)

        const reportData = await getReport(sessionId)
        if (cancelled) return

        setReport(reportData)
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : 'Failed to load session')
      } finally {
        if (cancelled) return
        setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [authReady, user, sessionId])

  if (!authReady) return <div className="p-6">Loading auth…</div>
  if (loading) return <div className="p-6">Loading session…</div>
  if (error) return <div className="p-6 text-red-500">{error}</div>

  return (
<div className="mx-auto max-w-7xl p-6 space-y-6">
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
    label="Focus Duration"
    value={session ? formatDuration(session.durationSeconds) : "—"}
  />
  <StatCard
    label="Total Focus Time"
    value={report ? formatDuration(report.totalFocusTime) : "—"}
  />
  <StatCard
    label="Focus Score"
    value={report ? `${focusScoreToPercent(report.avgFocusScore)}/100` : "—"}
  />
</div>
    </div>
  )
}