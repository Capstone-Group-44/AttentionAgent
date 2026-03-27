import { Target, Zap, Flame, Clock, Trophy } from "lucide-react";
import { LucideIcon } from "lucide-react";

export type UserStats = {
  sessions: number;
  gazeTime: number; // seconds
  avgScore: number; // 0–100
};

export type Badge = {
  id: string;
  label: string;
  description: string;
  icon: LucideIcon;
  color?: string;
  isUnlocked: (stats: UserStats) => boolean;
};

export const BADGES: Badge[] = [
  {
    id: "first_session",
    label: "Getting Started",
    description: "Complete your first session",
    icon: Target,
    color: "text-blue-500",
    isUnlocked: (s) => s.sessions >= 1,
  },
  {
    id: "sessions_10",
    label: "Committed",
    description: "Complete 10 sessions",
    icon: Zap,
    color: "text-yellow-500",
    isUnlocked: (s) => s.sessions >= 10,
  },
  {
    id: "sessions_50",
    label: "Locked In",
    description: "Complete 50 sessions",
    icon: Flame,
    color: "text-orange-500",
    isUnlocked: (s) => s.sessions >= 50,
  },
  {
    id: "gaze_1h",
    label: "Dialed In",
    description: "Accumulate 1 hour of gaze time",
    icon: Clock,
    color: "text-purple-500",
    isUnlocked: (s) => s.gazeTime >= 3600,
  },
  {
    id: "gaze_24h",
    label: "Marathoner",
    description: "Accumulate 24 hours of gaze time",
    icon: Clock,
    color: "text-indigo-500",
    isUnlocked: (s) => s.gazeTime >= 86400,
  },
  {
    id: "high_score",
    label: "High Performer",
    description: "Reach a 90+ average score",
    icon: Trophy,
    color: "text-green-600",
    isUnlocked: (s) => s.avgScore >= 90,
  },
];

export function getBadges(stats: UserStats) {
  return BADGES.map((badge) => ({
    ...badge,
    unlocked: badge.isUnlocked(stats),
  }));
}
