"use client";
import Image from "next/image";
import { ProgressCard } from "./_components/progress-card";
import { AchievementsCard } from "./_components/achievements-card";

import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { getFirstName } from "@/lib/utils"

// Homepage

export default function Home() {
  const { user, authReady } = useAuthUser()

  if (!authReady) return null

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans ">
      <main className="flex min-h-screen w-full max-w-6xl flex-col items-center justify-between py-10 px-16 bg-white  sm:items-start">
        <div className="flex max-w-6xl w-full justify-center flex-col gap-10">
      {user && (
        <div>
          <h1 className="text-2xl font-semibold">
            Welcome back, {getFirstName(user)}
          </h1>
          <p className="text-muted-foreground">
            Here’s your focus summary.
          </p>
        </div>
      )}
        <ProgressCard>

        </ProgressCard>
        <AchievementsCard/>
        </div>
      </main>
    </div>
  );
}
