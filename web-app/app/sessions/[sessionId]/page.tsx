'use client'

import { use } from 'react'
import { useEffect, useState } from 'react'
import { getSession, type Session } from '@/lib/api/sessions'
import { useAuthUser } from '@/lib/hooks/use-auth-user'
import { auth } from '@/lib/firebase'

export default function Page({
  params,
}: {
  params: Promise<{ sessionId: string }>
}) {
  const { sessionId } = use(params)
  const { user, authReady } = useAuthUser()

  const [session, setSession] = useState<Session | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    console.log('authReady:', authReady)
console.log('user uid:', user?.uid)
console.log('sessionId:', sessionId)


    if (!authReady) return // wait until firebase finishes loading auth state

    if (!user) {
      setError('Please log in to view this session.')
      return
    }

    console.log('getSession currentUser:', auth.currentUser?.uid)

    getSession(sessionId)
      .then(setSession)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load session'))
  }, [authReady, user, sessionId])

  if (!authReady) return <div className="p-6">Loading auth…</div>
  if (error) return <div className="p-6 text-red-500">{error}</div>
  if (!session) return <div className="p-6">Loading session…</div>

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold">Session Details</h1>
      <p className="mt-4">
        <strong>User ID:</strong> {session.userId}
      </p>
    </div>
  )
}
