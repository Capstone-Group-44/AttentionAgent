'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useAuthUser } from '@/lib/hooks/use-auth-user'
// TODO: replace with your real API
import { getUserSessions, type Session } from '@/lib/api/sessions'
import { formatDuration } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CalendarDays, ChevronRight } from 'lucide-react'

export function SessionHistory() {
  const { user, authReady } = useAuthUser()

  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      if (!authReady) return
      if (!user) {
        setSessions([])
        setLoading(false)
        return
      }

      setLoading(true)
      setError(null)

      try {
        const data = await getUserSessions(user.uid)
        if (!cancelled) setSessions(data)
      } catch (e) {
        if (!cancelled) setError('Failed to load sessions.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [authReady, user])

  if (loading) return <div className="text-sm opacity-70">Loading…</div>
  if (error) return <div className="text-sm text-red-600">{error}</div>
  if (!sessions.length) return <div className="text-sm opacity-70">No sessions yet.</div>


  return (
    <div className="mx-auto max-w-7xl p-6 ">
    <Card>
      <CardHeader className="flex flex-row items-center ">
        <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
          <CalendarDays size={20} />
        </div>
        <CardTitle className="text-base">Session History</CardTitle>
      </CardHeader>

      <CardContent className="p-0">
    <ul >
      {sessions.map((s) => (
        <li key={s.id}>
          <Link
  href={`/sessions/${s.id}`}
  className="flex items-center justify-between px-8 py-3 hover:bg-muted transition"
>
  <div>
    <div className="text-sm">
      {s.startTime.toDate().toLocaleString()}
    </div>
    <div className="text-xs opacity-70">
      {formatDuration(s.durationSeconds)}
    </div>
  </div>

<ChevronRight className="h-5 w-5 text-muted-foreground" />
</Link>
        </li>
      ))}
    </ul>
    </CardContent>
    </Card>
  </div>
  )
}
