import type { ColumnDef } from "@tanstack/react-table";
import type { SessionRow } from "@/lib/api/sessions";
import { formatDuration } from "@/lib/utils";

export const tstColumnDefs: ColumnDef<SessionRow>[] = [
  {
    id: "startTime",
    header: "Date",
    accessorFn: (r) => r.startTime.toDate(),
    cell: ({ getValue }) => {
      const date: Date = getValue<Date>();
      return date.toLocaleString();
    },
  },
  {
    id: "durationMinutes",
    header: "Duration (min)",
    accessorFn: (r) => Math.floor(r.durationSeconds / 60),
  },
  {
    id: "avgFocusScore",
    header: "Focus Score",
    accessorKey: "avgFocusScore",

    cell: ({ getValue }) => {
      const v = getValue<number>();
      return v < 0 ? "—" : `${v}/100`;
    },
  },
];
