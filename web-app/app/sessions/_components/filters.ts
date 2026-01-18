import { createColumnConfigHelper } from "@bazza-ui/filters";
import {
  CalendarArrowUpIcon,
  ClockIcon,
  PercentIcon,
  TagsIcon,
  CircleDotDashedIcon,
} from "lucide-react";
import type { SessionRow } from "@/lib/api/sessions";

const dtf = createColumnConfigHelper<SessionRow>();

export const columnsConfig = [
  // Date (startTime)
  dtf
    .date()
    .id("startTime")
    .accessor((row) => row.startTime.toDate())
    .displayName("Date")
    .icon(CalendarArrowUpIcon)
    .build(),

  // Duration
  dtf
    .number()
    .id("durationSeconds")
    .accessor((row) => row.durationSeconds)
    .displayName("Duration (sec)")
    .icon(ClockIcon)
    .min(0)
    .max(60 * 60 * 8)
    .build(),

  // Focus score
  dtf
    .number()
    .id("avgFocusScore")
    .accessor((row) => row.avgFocusScore)
    .displayName("Focus score")
    .icon(PercentIcon)
    .min(0)
    .max(100)
    .build(),
] as const;
