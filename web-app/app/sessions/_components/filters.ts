import { createColumnConfigHelper } from "@bazza-ui/filters";
import {
  CalendarArrowUpIcon,
  ClockIcon,
  PercentIcon,
  TagsIcon,
  CircleDotDashedIcon,
} from "lucide-react";
import type { SessionRow } from "@/lib/api/sessions";
import { formatDuration } from "@/lib/utils";

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
    .id("durationMinutes")
    .accessor((row) => row.durationSeconds / 60)
    .displayName("Duration (min)")
    .icon(ClockIcon)
    .min(0)
    .max(1440) // 24 hours
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
