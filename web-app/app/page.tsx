"use client";
import Image from "next/image";
import { ProgressCard } from "./_components/progress-card";
import { AchievementsCard } from "./_components/achievements-card";

import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { getFirstName } from "@/lib/utils"
import LandingPage from "./_components/landing-page";

// Homepage

export default function Home() {
  const { user, authReady } = useAuthUser()

  if (!authReady) return null

  if (!user) {
    return <LandingPage />;
  }

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
        {/* <AchievementsCard/> */}
        </div>

  );
}
