import { GoalsSettingsCard } from "@/components/goals-settings-card"

export default function SettingsPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Settings</h1>
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