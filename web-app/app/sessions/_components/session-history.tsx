import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SessionRow } from './session-row'

export function SessionHistory() {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-center gap-3">
        <CardTitle className="text-base font-semibold">Session History</CardTitle>
      </CardHeader>

      <CardContent className="p-0">

        <div className="grid grid-cols-[1fr_auto_auto_auto] gap-6 px-6 py-4 text-sm text-muted-foreground">
          <div />
          <div className="text-right">Duration</div>
          <div className="text-right">Sessions</div>
          <div className="text-right">Focus Score</div>
        </div>

        <div className="divide-y">
          {/* Skeleton rows for layout/testing */}
          <SessionRow sessionId="3454365"/>
          <SessionRow sessionId="2345245"/>
          <SessionRow sessionId="6767546"/>
          <SessionRow sessionId="8653423"/>
          <SessionRow sessionId="9487237"/>
        </div>
      </CardContent>
    </Card>
  )
}
