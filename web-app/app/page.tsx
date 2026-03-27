"use client";
import Image from "next/image";
import { ProgressCard } from "./_components/progress-card";
import { AchievementsCard } from "./_components/achievements-card";

import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { getFirstName } from "@/lib/utils"
import LandingPage from "./_components/landing-page";
import { useUserSessionRows } from "@/lib/hooks/queries/session-rows";
import { focusScoreToPercent } from "@/lib/utils";

// Homepage

export default function Home() {
  const { user, authReady } = useAuthUser()
  const sessionsQ = useUserSessionRows(user?.uid);

  if (!authReady) return null

  if (!user) {
    return <LandingPage />;
  }
  

  if (sessionsQ.isLoading) return null;

  const sessions = sessionsQ.data ?? [];
  const totalSessions = sessions.length;

const totalGazeTime = sessions.reduce(
  (sum, s) => sum + (s.durationSeconds ?? 0),
  0
);

const avgScore =
  sessions.length === 0
    ? 0
    : focusScoreToPercent(
        sessions.reduce((sum, s) => sum + (s.avgFocusScore ?? 0), 0) /
          sessions.length
      );

  return (
           <div className="flex  justify-center flex-col gap-10">
      {user && (
        <div>
          <h1 className="text-2xl font-semibold">
            Welcome back, {getFirstName(user)}
          </h1>
          <p className="text-muted-foreground">
            Here’s your screen gaze activity summary.
          </p>
        </div>
      )}
        <ProgressCard>

        </ProgressCard>
       <AchievementsCard
  sessions={totalSessions}
  gazeTime={totalGazeTime}
  avgScore={avgScore}
/>
        </div>

  );
}
