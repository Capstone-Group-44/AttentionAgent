"use client";
import { StatCard } from "@/components/stat-card";
// import { SessionHistoryList } from "./_components/session-history-list";
import { calcAvgFocusScore, calcTotalFocusTime, formatDuration } from "@/lib/utils";
import { getUserReports } from "@/lib/api/reports";
import { getUserSessions, getUserSessionRows, Session } from "@/lib/api/sessions";
import { useAuthUser } from "@/lib/hooks/use-auth-user";
import { ChevronRight, Clock, Layers, TrendingUp } from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import { Filter } from '@/components/ui/filter'
import { columnsConfig } from "./_components/filters";
import { useDataTableFilters } from "@bazza-ui/filters";
import { set } from "date-fns";
import type { Report } from "@/lib/api/reports";
import type { SessionRow } from "@/lib/api/sessions"
import type { FiltersState} from '@bazza-ui/filters'
import Link from "next/link"
import { createTSTColumns, createTSTFilters } from '@bazza-ui/filters/tanstack-table'
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
} from '@tanstack/react-table'
import { tstColumnDefs } from "./_components/tst-columns";


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
        getUserSessionRows(userId),
        getUserReports(userId),
      ])

      setSessionRows(sessionsData)
      console.log("sessionsData", sessionsData)
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

      {/* Tanstack table */}

      <div className="rounded-lg border overflow-hidden">
  <table className="w-full text-sm">
    <thead className="bg-muted/40">
      {table.getHeaderGroups().map((headerGroup) => (
        <tr key={headerGroup.id} className="border-b">
          {headerGroup.headers.map((header) => (
            <th
              key={header.id}
              className="text-left font-medium text-muted-foreground px-6 py-3"
            >
              {header.isPlaceholder
                ? null
                : flexRender(header.column.columnDef.header, header.getContext())}
            </th>
          ))}
        </tr>
      ))}
    </thead>

    <tbody>
      {table.getRowModel().rows.map((row) => (
        <tr key={row.id} className="border-b last:border-b-0 hover:bg-muted/30">
          {row.getVisibleCells().map((cell) => (
            <td key={cell.id} className="px-6 py-3">
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  </table>
</div>

    </div>
  )}