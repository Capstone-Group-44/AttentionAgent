'use client'

import { StatRing } from "@/components/stat-ring";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { formatDuration } from "@/lib/utils";
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

  if (!authReady || loading) {
    return <div>Loading...</div>
  }

  // Fixed goals for now
  const sessionsGoal = 6
  const focusGoalSeconds = 4 * 3600
  const focusScoreGoal = 90

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
            percent={0}
            colourClass="stroke-blue-600"
          />

          <StatRing 
            label={"Focus Time"} 
            value={formatDuration(focusSecondsToday)} 
            percent={0}
            colourClass="stroke-purple-600"
          />

          <StatRing
            label="Average Focus Score"
            value={
              <span>
                {avgFocusScoreToday}
                <span> / 100</span>
              </span>
            }
            percent={0}
            colourClass="stroke-green-600"
          />

          </div>
        </CardContent>
    </Card>

  )
}
