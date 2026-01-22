'use client'

import { StatRing } from "@/components/stat-ring";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { focusScoreToPercent, formatDuration } from "@/lib/utils";
import { useTodayProgress } from "@/lib/hooks/use-today-progress";

export function ProgressCard() {
  // const focusSecondsToday = 10800 // Example: 3 hours in seconds
  // const numberSessionsToday = 5
  // const avgFocusScoreToday = 85 // Example: 85%
  
  const { user, authReady } = useAuthUser()
  const { stats, loading } = useTodayProgress(user?.uid)

  const focusSecondsToday = stats.focusSecondsToday
  const sessionsToday = stats.sessionsToday
  const avgFocusScoreToday = stats.avgFocusScoreToday ?? 0

   // stats.avgFocusScoreToday is 0–1, convert to 0–100 for UI
  const avgFocusScorePercent =
    stats.avgFocusScoreToday == null ? 0 : focusScoreToPercent(stats.avgFocusScoreToday)

  if (!authReady || loading) {
    return <div>Loading...</div>
  }

  // Fixed goals for now
  const sessionsGoal = 6
  const focusGoalSeconds = 1 * 3600
  const focusScoreGoal = 95

  const sessionsPercent = (sessionsToday / sessionsGoal) * 100
  const focusPercent = (focusSecondsToday / focusGoalSeconds) * 100
  const focusScorePercent = (avgFocusScorePercent / focusScoreGoal) * 100

  return (
    <Card className="">
    <CardHeader>
            <CardTitle>Today's Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 sm:grid-cols-3 justify-items-center">

          
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
            label={"Focus Time"} 
            value={formatDuration(focusSecondsToday)} 
            percent={focusPercent}
            colourClass="stroke-purple-600"
            goal={formatDuration(focusGoalSeconds)}
          />

          <StatRing
            label="Average Focus Score"
            value={
              <span>
                {avgFocusScorePercent}
                <span> / 100</span>
              </span>
            }
            percent={focusScorePercent}
            colourClass="stroke-green-600"
            goal={<span>
                {focusScoreGoal}
                <span> / 100</span>
              </span>}
          />

          </div>
        </CardContent>
    </Card>

  )
}
