"use client";
import { StatCard } from "@/components/stat-card";
import { calcAvgFocusScore, calcTotalFocusTime, formatDuration } from "@/lib/utils";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { ChevronRight, Clock, Layers, TrendingUp } from "lucide-react";
import { useMemo } from "react";
import { Filter } from '@/components/ui/filter'
import { columnsConfig } from "./_components/filters";
import { useDataTableFilters } from "@bazza-ui/filters";
import { createTSTColumns, createTSTFilters } from '@bazza-ui/filters/tanstack-table'
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table'
import { tstColumnDefs } from "./_components/tst-columns";
import { useRouter } from "next/navigation";
import { useUserReports } from "@/lib/hooks/queries/reports";
import { useUserSessionRows } from "@/lib/hooks/queries/session-rows";
import { SessionHistoryTable } from "./_components/session-history-table";


export default function SessionsPage(){
  const router = useRouter();

  const { user, authReady } = useAuthUser()
  const userId = user?.uid

  const sessionRowsQ = useUserSessionRows(userId)
  const reportsQ = useUserReports(userId)

  // Safe defaults so we can still call table/filter hooks
  const sessionRows = sessionRowsQ.data ?? []
  const reports = reportsQ.data ?? []

  const sessionCount = sessionRows.length
  const totalFocus = calcTotalFocusTime(reports)
  const avgFocus = calcAvgFocusScore(reports)


  const { columns, filters, actions, strategy } = useDataTableFilters({
  strategy: 'client', 
  data: sessionRows ?? [],    
  columnsConfig,
  // filters: filtersState,
  // onFiltersChange: setFiltersState,
  defaultFilters: []
  })

  // Create TST-compatible columns with filter functions
  const tstColumns = useMemo(
    () =>
      createTSTColumns({
        columns: tstColumnDefs, 
        configs: columns, // columns from useDataTableFilters       
      }),
    [columns],
  )

  // Convert filter state to TST format
  const tstFilters = useMemo(
    () => createTSTFilters(filters),
    [filters]
  )

  const table = useReactTable({
    data: sessionRows ?? [],
    columns: tstColumns,
    getRowId: (row) => row.id,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      columnFilters: tstFilters
    }
  })

// some error handling

if (!authReady) return <div className="p-6">Loading auth…</div>
if (!user) return <div className="p-6 text-red-500">Please log in.</div>
if (sessionRowsQ.isLoading || reportsQ.isLoading) return <div className="p-6">Loading…</div>
if (sessionRowsQ.error || reportsQ.error) return <div className="p-6 text-red-500">Failed to load data.</div>


return (
    <div className="space-y-6">

      <h1 className="text-xl font-semibold">Overall Progress</h1>

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

      {/* Session History Table */}

      <h1 className="text-xl font-semibold">Session History</h1>

      <SessionHistoryTable
        sessionRows={sessionRows}
        onRowClick={(sessionId) => {
          router.push(`/sessions/${sessionId}`)
        }}
      />
    </div>
  )}