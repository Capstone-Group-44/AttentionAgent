import { clsx, type ClassValue } from "clsx";
import { Timestamp } from "firebase/firestore";
import { twMerge } from "tailwind-merge";

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

export function focusScoreToPercent(score: number): number {
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
