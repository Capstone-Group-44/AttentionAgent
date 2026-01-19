import { clsx, type ClassValue } from "clsx";
import { Timestamp } from "firebase/firestore";
import { twMerge } from "tailwind-merge";
import ms, { type StringValue } from "ms";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const rem = s % 60;

  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${rem}s`;
  return `${rem}s`;
}

export function formatSessionDate(ts: Timestamp): string {
  const date = ts.toDate();

  return date.toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatSessionDateTime(ts: Timestamp): string {
  const date = ts.toDate();

  return date.toLocaleString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function focusScoreToPercent(score: number) {
  if (Number.isNaN(score)) return 0;
  return Math.round(score * 100);
}

export function getFirstName(user: {
  displayName?: string | null;
  email?: string | null;
}) {
  if (user.displayName) {
    return user.displayName.split(" ")[0];
  }

  if (user.email) {
    return user.email.split("@")[0];
  }

  return "there";
}

export function calcTotalFocusTime(reports: { totalFocusTime: number }[]) {
  return reports.reduce((sum, r) => sum + r.totalFocusTime, 0);
}

export function calcAvgFocusScore(reports: { avgFocusScore: number }[]) {
  if (!reports.length) return null;
  const avg =
    reports.reduce((sum, r) => sum + r.avgFocusScore, 0) / reports.length;
  return Math.round(avg * 100);
}

export function secondsToMinutes(seconds: number): number {
  return Math.floor(seconds / 60);
}

export type DurationUnit = "milliseconds" | "seconds" | "minutes" | "hours";

/**
 * Parses user input like "1h", "60 mins", "2.5 hours", "90s"
 * into a NUMBER in the requested unit.
 *
 * If input is just "12" (no unit), we treat it as already in the unit.
 */
export function parseDurationToUnit(
  input: string,
  unit: Exclude<DurationUnit, "milliseconds"> // seconds/minutes/hours
): number | null {
  const raw = input.trim().toLowerCase();
  if (!raw) return null;

  // If user typed only a number, treat as already in the target unit
  if (/^\d+(\.\d+)?$/.test(raw)) return Number(raw);

  // Otherwise parse with ms()
  const parsed = ms(raw as StringValue);
  if (typeof parsed !== "number" || !Number.isFinite(parsed)) return null;

  switch (unit) {
    case "seconds":
      return parsed / 1000;
    case "minutes":
      return parsed / 60000;
    case "hours":
      return parsed / 3600000;
  }
}
