"use client";
import { StatCard } from "@/components/stat-card";
// import { SessionHistoryList } from "./_components/session-history-list";
import { calcAvgFocusScore, calcTotalFocusTime, formatDuration } from "@/lib/utils";
import { getUserReports } from "@/lib/api/reports";
import { getUserSessions, Session } from "@/lib/api/sessions";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { Clock, Layers, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
import { Filter } from '@/components/ui/filter'
import { columnsConfig } from "./_components/filters";
import { useDataTableFilters } from "@bazza-ui/filters";
import { set } from "date-fns";
import type { Report } from "@/lib/api/reports";
import type { SessionRow } from "@/lib/api/sessions"
import type { FiltersState} from '@bazza-ui/filters'


export default function SessionsPage(){
    const { user, authReady } = useAuthUser()

  const [totalFocus, setTotalFocus] = useState(0)
  const [avgFocus, setAvgFocus] = useState<number | null>(null)
  const [sessionCount, setSessionCount] = useState(0)
  const [sessionRows, setSessionRows] = useState<SessionRow[]>([])

  const [filtersState, setFiltersState] = useState<FiltersState>([])

  useEffect(() => {
    if (!authReady || !user) return

    const userId = user.uid
    async function loadStats() {
      const [sessionsData, reportsData] = await Promise.all([
        getUserSessions(userId),
        getUserReports(userId),
      ])

      setSessionRows(sessionRows)
      setSessionCount(sessionsData.length)

      const total = calcTotalFocusTime(reportsData);
      setTotalFocus(total)

      setAvgFocus(calcAvgFocusScore(reportsData))
    }

    loadStats()
  }, [authReady, user])

  const { columns, filters, actions, strategy } = useDataTableFilters({
  strategy: 'client', 
  data: sessionRows ?? [],    
  columnsConfig,
  // filters: filtersState,
  // onFiltersChange: setFiltersState,
  defaultFilters: []
})


return (
    <div className="space-y-6">

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total Focus Time"
          value={formatDuration(totalFocus)}
          icon={Clock}
        />
        <StatCard
          label="Total Sessions"
          value={sessionCount}
          icon={Layers}
        />
        <StatCard
          label="Avg Focus Score"
          value={avgFocus === null ? "—" : `${avgFocus}/100`}
          icon={TrendingUp}
        />
      </div>
{/* 
      <SessionHistoryList /> */}

      {/* Filter Table */}

      <Filter.Provider
        columns={columns}
        filters={filters}
        actions={actions}
        strategy={strategy}
      >
        <Filter.Root>
          <div className="flex items-center gap-2">
            <Filter.Menu />
            <Filter.List>
              {({ filter, column }) => (
                <Filter.Item filter={filter} column={column}>
                  <Filter.Subject />
                  <Filter.Operator />
                  <Filter.Value />
                  <Filter.Remove />
                </Filter.Item>
              )}
            </Filter.List>
          </div>
          <Filter.Actions />
        </Filter.Root>
      </Filter.Provider>

    </div>
  )}