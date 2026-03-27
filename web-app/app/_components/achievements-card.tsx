"use client";

import { CardTitle } from "@/components/ui/card";
import { getBadges } from "@/lib/badges";
import { Lock, Trophy } from "lucide-react";

type Props = {
  sessions: number;
  gazeTime: number;
  avgScore: number;
};

export function AchievementsCard({ sessions, gazeTime, avgScore }: Props) {
  const badges = getBadges({ sessions, gazeTime, avgScore });

  return (
    <div className="rounded-xl border p-6 bg-white shadow-sm">
      <CardTitle className="mb-4">Achievements</CardTitle>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {badges.map((badge) => (
          <div
            key={badge.id}
            className={`p-4 rounded-lg border text-center transition
              ${badge.unlocked ? "bg-green-50 border-green-200" : "bg-gray-50 opacity-50"}
            `}
          >
            <div className="mb-2 flex justify-center">
  {badge.unlocked ? (
    <Trophy className="w-6 h-6 text-green-600" />
  ) : (
    <Lock className="w-6 h-6 text-gray-400" />
  )}
</div>

            <p className="text-sm font-medium">{badge.label}</p>
            <p className="text-xs text-gray-500">{badge.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}