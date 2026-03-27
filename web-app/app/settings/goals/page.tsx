import { GoalsSettingsCard } from "@/components/goals-settings-card"

export default function GoalsPage() {
  return (
    <main className="mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Goals</h1>
        <p className="text-muted-foreground">
          Manage your preferences and daily goals.
        </p>
      </div>

      <div className="space-y-6">
        <GoalsSettingsCard />
      </div>
    </main>
  )
}