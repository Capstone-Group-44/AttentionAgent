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

      {/* Session History header */}

      <h1 className="text-xl font-semibold">Session History</h1>



      {/* Filter */}

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
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </th>
                ))}

                {/* Arrow column header */}
                <th className="w-4 px-0 py-3"></th>
              </tr>
            ))}
          </thead>


          <tbody>
            {table.getRowModel().rows.map((row) => {
              const sessionId = row.original.id;

              return (
                <tr
                  key={row.id}
                  role="link"
                  tabIndex={0}
                  onClick={() => router.push(`/sessions/${sessionId}`)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      router.push(`/sessions/${sessionId}`);
                    }
                  }}
                  className="border-b last:border-b-0 hover:bg-muted/30 cursor-pointer"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-6 py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}

                  {/* Arrow indicator */}
                  <td className="pr-4 py-3 text-right text-muted-foreground">
                    <ChevronRight className="h-4 w-4" />
                  </td>
                </tr>
              );
            })}
          </tbody>


        </table>
    </div>

    </div>
  )}