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

export function parseDurationInput(
  input: string,
  unit: "seconds" | "minutes" | "hours"
): number | null {
  const trimmed = input.trim().toLowerCase();
  if (!trimmed) return null;

  // If it's a plain number, interpret as minutes
  if (/^\d+(\.\d+)?$/.test(trimmed)) {
    const minutes = Number(trimmed);
    switch (unit) {
      case "seconds":
        return minutes * 60;
      case "minutes":
        return minutes;
      case "hours":
        return minutes / 60;
    }
  }

  const parsedMs = ms(trimmed as StringValue);
  if (typeof parsedMs !== "number") return null;

  switch (unit) {
    case "seconds":
      return parsedMs / 1000;
    case "minutes":
      return parsedMs / 60000;
    case "hours":
      return parsedMs / 3600000;
  }
}
