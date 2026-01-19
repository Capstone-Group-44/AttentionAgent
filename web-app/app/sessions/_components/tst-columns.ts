import type { ColumnDef } from "@tanstack/react-table";
import type { SessionRow } from "@/lib/api/sessions";
import { formatDuration, formatSessionDateTime } from "@/lib/utils";
import { Timestamp } from "firebase/firestore";

export const tstColumnDefs: ColumnDef<SessionRow>[] = [
  {
    id: "startTime",
    header: "Date",
    accessorFn: (r) => r.startTime, // Timestamp
    cell: ({ getValue }) => {
      const ts = getValue<Timestamp>();
      return formatSessionDateTime(ts);
    },
  },
  {
    id: "durationMinutes",
    header: "Duration (min)",
    accessorFn: (r) => Math.floor(r.durationSeconds / 60),
  },
  {
    id: "avgFocusScore",
    header: "Focus",
    accessorKey: "avgFocusScore",

    cell: ({ getValue }) => {
      const v = getValue<number>();
      return v < 0 ? "—" : `${v}/100`;
    },
  },
];
