"use client"

import { StatRing } from "@/components/stat-ring"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { useTodayProgress } from "@/lib/hooks/use-today-progress"
import { useUserGoals } from "@/lib/hooks/use-user-goals"
import { focusScoreToPercent, formatDuration } from "@/lib/utils"

export function ProgressCard() {
  const { user, authReady } = useAuthUser()
  const { stats, loading } = useTodayProgress(user?.uid)
  const { goals, loading: goalsLoading } = useUserGoals(user?.uid)

  const focusSecondsToday = stats.focusSecondsToday
  const sessionsToday = stats.sessionsToday

  const avgFocusScorePercent =
    stats.avgFocusScoreToday == null
      ? 0
      : focusScoreToPercent(stats.avgFocusScoreToday)

  if (!authReady || loading || goalsLoading) {
    return <div>Loading...</div>
  }

  const sessionsGoal = goals.sessionsGoal
  const focusGoalSeconds = goals.focusGoalSeconds
  const focusScoreGoal = goals.focusScoreGoal

  const sessionsPercent =
    sessionsGoal > 0 ? Math.min((sessionsToday / sessionsGoal) * 100, 100) : 0

  const focusPercent =
    focusGoalSeconds > 0
      ? Math.min((focusSecondsToday / focusGoalSeconds) * 100, 100)
      : 0

  const focusScorePercent =
    focusScoreGoal > 0
      ? Math.min((avgFocusScorePercent / focusScoreGoal) * 100, 100)
      : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Today's Progress</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="grid gap-6 justify-items-center sm:grid-cols-3">
          <StatRing
            label="Sessions"
            value={
              <span>
                {sessionsToday}
                <span> Completed</span>
              </span>
            }
            percent={sessionsPercent}
            colourClass="stroke-blue-600"
            goal={sessionsGoal}
          />

          <StatRing
            label="Gaze Time"
            value={formatDuration(focusSecondsToday)}
            percent={focusPercent}
            colourClass="stroke-purple-600"
            goal={formatDuration(focusGoalSeconds)}
          />

          <StatRing
            label="Average Gaze Score"
            value={
              <span>
                {avgFocusScorePercent}
                <span> / 100</span>
              </span>
            }
            percent={focusScorePercent}
            colourClass="stroke-green-600"
            goal={
              <span>
                {focusScoreGoal}
                <span> / 100</span>
              </span>
            }
          />
        </div>
      </CardContent>
    </Card>
  )
}