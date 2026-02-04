"use client";

import { useMemo } from "react";
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
} from "@tanstack/react-table";
import { tstColumnDefs } from "./tst-columns";
import type { SessionRow } from "@/lib/api/sessions";

type SessionHistoryTableProps<T extends { id: string }> = {
  sessionRows: SessionRow[];
  onRowClick: (sessionId: string) => void;
};

export function SessionHistoryTable<T extends { id: string }>({
  sessionRows,
  onRowClick,
}: SessionHistoryTableProps<T>) {
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

  const table = useReactTable({
    data: sessionRows,
    columns: tstColumns,
    getRowId: (row) => row.id,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      columnFilters: tstFilters,
    },
  });

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
                <th className="w-4 px-0 py-3" />
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
                  onClick={() => onRowClick(sessionId)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onRowClick(sessionId);
                    }
                  }}
                  className="border-b last:border-b-0 hover:bg-muted/30 cursor-pointer"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-6 py-3">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}

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
  );
}
