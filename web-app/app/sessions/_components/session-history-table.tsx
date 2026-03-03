"use client";

import { useEffect, useMemo, useState } from "react";
import { ChevronRight } from "lucide-react";
import { Filter } from "@/components/ui/filter";
import { columnsConfig } from "./filters";
import { useDataTableFilters } from "@bazza-ui/filters";
import {
  createTSTColumns,
  createTSTFilters,
} from "@bazza-ui/filters/tanstack-table";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
  getPaginationRowModel,
  getSortedRowModel,
} from "@tanstack/react-table";
import type { SortingState } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react";
import { tstColumnDefs } from "./tst-columns";
import type { SessionRow } from "@/lib/api/sessions";

type FilteredSummary = {
  totalSessions: number;
  avgFocusScore: number | null;
};

type SessionHistoryTableProps = {
  sessionRows: SessionRow[];
  onRowClick: (sessionId: string) => void;
  onFilteredSummaryChange?: (summary: FilteredSummary | null) => void;
};

export function SessionHistoryTable({
  sessionRows,
  onRowClick,
  onFilteredSummaryChange,
}: SessionHistoryTableProps) {
  const { columns, filters, actions, strategy } = useDataTableFilters({
    strategy: "client",
    data: sessionRows,
    columnsConfig,
    defaultFilters: [],
  });

  const tstColumns = useMemo(
    () =>
      createTSTColumns({
        columns: tstColumnDefs,
        configs: columns,
      }),
    [columns]
  );

  const tstFilters = useMemo(() => createTSTFilters(filters), [filters]);

  const [pagination, setPagination] = useState({
  pageIndex: 0,
  pageSize: 10,
});

const [sorting, setSorting] = useState<SortingState>([
  { id: "startTime", desc: true },
]);

  const table = useReactTable({
    data: sessionRows,
    columns: tstColumns,
    getRowId: (row) => row.id,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onPaginationChange: setPagination,
    onSortingChange: setSorting,
    state: {
      columnFilters: tstFilters,
      pagination,
      sorting,
    },
  });

  const filteredRows = table.getFilteredRowModel().rows;
const filtersActive = tstFilters.length > 0; 

const filteredSummary = useMemo<FilteredSummary>(() => {
  const rows = filteredRows.map(r => r.original);

  const totalSessions = rows.length;

  // use sessionRows avgFocusScore field
  const scores = rows
    .map(r => r.avgFocusScore)
    .filter((v): v is number => typeof v === "number" && v >= 0);

  const avgFocusScore =
    scores.length === 0 ? null : Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);

  return { totalSessions, avgFocusScore };
}, [filteredRows]);

useEffect(() => {
  onFilteredSummaryChange?.(filtersActive ? filteredSummary : null);
}, [filtersActive, filteredSummary, onFilteredSummaryChange]);



  useEffect(() => {
  setPagination((p) => ({ ...p, pageIndex: 0 }));
}, [tstFilters]);

 // reset to page 1 when filters/sorting change
useEffect(() => {
  setPagination((p) => ({ ...p, pageIndex: 0 }));
}, [tstFilters, sorting]);



  return (
    <div className="space-y-4">
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

      <div className="rounded-lg border overflow-hidden">
        <div className="rounded-lg border overflow-hidden bg-background">
  <table className="w-full text-sm">
    <thead className="bg-muted/40">
      {table.getHeaderGroups().map((headerGroup) => (
        <tr key={headerGroup.id} className="border-b">
          {headerGroup.headers.map((header) => {
            const id = header.column.id;
            const isNumeric = id === "duration" || id === "focusScore";

            return (
              <th
  key={header.id}
  className={[
    "px-4 py-3 text-xs font-medium uppercase tracking-wide text-muted-foreground",
    isNumeric ? "text-right" : "text-left",
  ].join(" ")}
>
  {header.isPlaceholder ? null : (
    <button
      type="button"
      className={[
        "inline-flex items-center gap-1 select-none",
        header.column.getCanSort() ? "cursor-pointer" : "cursor-default",
        isNumeric ? "ml-auto" : "",
      ].join(" ")}
      onClick={header.column.getToggleSortingHandler()}
      disabled={!header.column.getCanSort()}
      aria-label={`Sort by ${String(header.column.id)}`}
    >
      {flexRender(header.column.columnDef.header, header.getContext())}
      {header.column.getCanSort() && (
        <ArrowUpDown className="h-3.5 w-3.5 opacity-60" />
      )}
    </button>
  )}
</th>

            );
          })}

          {/* chevron header cell to keep alignment */}
          <th className="w-10 px-2 py-3" />
        </tr>
      ))}
    </thead>

    <tbody>
      {table.getPaginationRowModel().rows.map((row) => {
        const sessionId = row.original.id;

        return (
          <tr
            key={row.id}
            role="link"
            tabIndex={0}
            onClick={() => onRowClick(sessionId)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onRowClick(sessionId);
              }
            }}
            className="border-b last:border-b-0 hover:bg-muted/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {row.getVisibleCells().map((cell) => {
              const id = cell.column.id;
              const isNumeric = id === "duration" || id === "focusScore";

              return (
                <td
                  key={cell.id}
                  className={[
                    "px-4 py-3 align-middle",
                    isNumeric ? "text-right tabular-nums" : "text-left",
                  ].join(" ")}
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              );
            })}

            <td className="w-10 px-2 py-3 align-middle text-right text-muted-foreground">
              <ChevronRight className="h-4 w-4 inline-block" />
            </td>
          </tr>
        );
      })}
    </tbody>
  </table>

  {/* footer */}
  <div className="flex flex-wrap items-center justify-between gap-3 border-t bg-muted/20 px-4 py-3">
    <div className="text-sm text-muted-foreground">
      Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
    </div>

    <div className="flex items-center gap-2">
      <button
        className="h-9 rounded-md border bg-background px-3 text-sm disabled:opacity-50"
        onClick={() => table.previousPage()}
        disabled={!table.getCanPreviousPage()}
      >
        Prev
      </button>

      <button
        className="h-9 rounded-md border bg-background px-3 text-sm disabled:opacity-50"
        onClick={() => table.nextPage()}
        disabled={!table.getCanNextPage()}
      >
        Next
      </button>

      <select
        className="h-9 rounded-md border bg-background px-2 text-sm"
        value={table.getState().pagination.pageSize}
        onChange={(e) => table.setPageSize(Number(e.target.value))}
      >
        {[10, 20, 50].map((size) => (
          <option key={size} value={size}>
            {size} / page
          </option>
        ))}
      </select>
    </div>
  </div>
</div>

        
      </div>
      
    </div>
  );
}