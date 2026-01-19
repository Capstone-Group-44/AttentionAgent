import type { ColumnDef } from "@tanstack/react-table";
import type { SessionRow } from "@/lib/api/sessions";
import { formatDateTime } from "@/lib/utils";
import { Timestamp } from "firebase/firestore";

export const tstColumnDefs: ColumnDef<SessionRow>[] = [
  {
    id: "startTime",
    header: "Date",
    accessorFn: (r) => r.startTime.toDate(), // Timestamp
    cell: ({ getValue }) => formatDateTime(getValue<Date>()),
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
