'use client'

import { StatRing } from "@/components/stat-ring";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDuration } from "@/lib/utils";

export function ProgressCard() {
  const focusSecondsToday = 10800 // Example: 3 hours in seconds
  const numberSessionsToday = 5
  const avgFocusScoreToday = 85 // Example: 85%
  return (
    <Card className="">
    <CardHeader>
            <CardTitle>Today's Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 sm:grid-cols-3 justify-items-center">

          <StatRing label={"Focus Time"} value={formatDuration(focusSecondsToday)} percent={0}/>
          <StatRing
            label="Sessions"
            value={
              <span>
                {numberSessionsToday}
                <span> Completed</span>
              </span>
            }
            percent={0}
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
          />

          </div>
        </CardContent>
    </Card>

  )
}
