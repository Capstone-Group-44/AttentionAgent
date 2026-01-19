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

export function formatDateTime(date: Date) {
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

export type DurationUnit = "seconds" | "minutes" | "hours";

function detectInputUnit(raw: string): DurationUnit | null {
  if (/\b(h|hr|hrs|hour|hours)\b/.test(raw)) return "hours";
  if (/\b(m|min|mins|minute|minutes)\b/.test(raw)) return "minutes";
  if (/\b(s|sec|secs|second|seconds)\b/.test(raw)) return "seconds";
  return null;
}

function pluralize(unit: DurationUnit, n: number) {
  const one =
    unit === "hours" ? "hour" : unit === "minutes" ? "minute" : "second";
  return Math.abs(n) === 1 ? one : `${one}s`;
}

function msToUnit(msValue: number, unit: DurationUnit): number {
  switch (unit) {
    case "seconds":
      return msValue / 1000;
    case "minutes":
      return msValue / 60000;
    case "hours":
      return msValue / 3600000;
  }
}

/**
 * Parses user input like "1h", "60 mins", "2.5 hours", "90s"
 * into a number in the requested unit.
 *
 * If input is just "12" (no unit), we treat it as already in the unit.
 */

export function parseDurationToUnit(
  input: string,
  baseUnit: DurationUnit
): { value: number; display: string } | null {
  const raw = input.trim().toLowerCase();
  if (!raw) return null;

  // Plain number: treat as base unit for both storage + display
  if (/^\d+(\.\d+)?$/.test(raw)) {
    const n = Number(raw);
    const unitLabel = pluralize(baseUnit, n);
    return { value: n, display: `${n} ${unitLabel}` };
  }

  const parsedMs = ms(raw as StringValue);
  if (typeof parsedMs !== "number") return null;

  // store in base unit
  const storedValue = msToUnit(parsedMs, baseUnit);

  // display in the unit the user typed (hours/minutes/seconds) if we can detect it
  const displayUnit = detectInputUnit(raw) ?? baseUnit;
  const displayValue = msToUnit(parsedMs, displayUnit);

  // rounding for nicer menu
  const rounded =
    Math.abs(displayValue) >= 10
      ? Math.round(displayValue)
      : Math.round(displayValue * 100) / 100;

  const unitLabel = pluralize(displayUnit, rounded);

  return {
    value: storedValue,
    display: `${rounded} ${unitLabel}`,
  };
}
