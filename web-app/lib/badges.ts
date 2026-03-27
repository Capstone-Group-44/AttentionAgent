export type UserStats = {
  sessions: number;
  gazeTime: number; // seconds
  avgScore: number; // 0–100
};

export type Badge = {
  id: string;
  label: string;
  description: string;
  isUnlocked: (stats: UserStats) => boolean;
};

export const BADGES: Badge[] = [
  {
    id: "first_session",
    label: "Getting Started",
    description: "Complete your first session",
    isUnlocked: (s) => s.sessions >= 1,
  },
  {
    id: "sessions_10",
    label: "Committed",
    description: "Complete 10 sessions",
    isUnlocked: (s) => s.sessions >= 10,
  },
  {
    id: "sessions_50",
    label: "Locked In",
    description: "Complete 50 sessions",
    isUnlocked: (s) => s.sessions >= 50,
  },
  {
    id: "gaze_1h",
    label: "Dialed In",
    description: "Accumulate 1 hour of gaze time",
    isUnlocked: (s) => s.gazeTime >= 3600,
  },
  {
    id: "gaze_24h",
    label: "Marathoner",
    description: "Accumulate 24 hours of gaze time",
    isUnlocked: (s) => s.gazeTime >= 86400,
  },
  {
    id: "high_score",
    label: "High Performer",
    description: "Reach a 90+ average score",
    isUnlocked: (s) => s.avgScore >= 90,
  },
];

export function getBadges(stats: UserStats) {
  return BADGES.map((badge) => ({
    ...badge,
    unlocked: badge.isUnlocked(stats),
  }));
}
