import Image from "next/image";
import { ProgressCard } from "./_components/progress-card";
import { AchievementsCard } from "./_components/achievements-card";

// Homepage

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-6xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <div className="flex max-w-6xl w-full justify-center flex-col gap-10">
        <ProgressCard>

        </ProgressCard>
        <AchievementsCard/>
        </div>
      </main>
    </div>
  );
}
