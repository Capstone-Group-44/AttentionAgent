"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"

import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { saveUserGoals } from "@/lib/api/goals"
import { useUserGoals } from "@/lib/hooks/use-user-goals"
import { Slider } from "@/components/ui/slider"
import { GoalRingInput } from "./goal-ring-input"

const formSchema = z.object({
  sessionsGoal: z.number().int().min(1, "Must be at least 1"),
  focusGoalMinutes: z.number().int().min(5, "Must be at least 5 minutes"),
  focusScoreGoal: z.number().int().min(1, "Must be at least 1").max(100, "Must be 100 or less"),
})

type FormValues = z.infer<typeof formSchema>

export function GoalsSettingsCard() {
  const [saving, setSaving] = useState(false)

  const { user } = useAuthUser()
  const { goals, loading } = useUserGoals(user?.uid)
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sessionsGoal: 6,
      focusGoalMinutes: 60,
      focusScoreGoal: 95,
    },
  })

  useEffect(() => {
    form.reset({
      sessionsGoal: goals.sessionsGoal,
      focusGoalMinutes: Math.floor(goals.focusGoalSeconds / 60),
      focusScoreGoal: goals.focusScoreGoal,
    })
  }, [goals, form])

async function onSubmit(values: FormValues) {
  if (!user?.uid) return

  try {
    setSaving(true)

    await saveUserGoals(user.uid, {
      sessionsGoal: values.sessionsGoal,
      focusGoalSeconds: values.focusGoalMinutes * 60,
      focusScoreGoal: values.focusScoreGoal,
    })
  } catch (error) {
    console.error("Failed to save goals:", error)
  } finally {
    setSaving(false)
  }
}

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Goals</CardTitle>
        <p className="text-sm text-muted-foreground">
          Set the targets used in your dashboard progress summary.
        </p>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
  <div className="max-w-md space-y-6">
              <FormField
                control={form.control}
                name="sessionsGoal"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sessions goal</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        name={field.name}
                        ref={field.ref}
                        onBlur={field.onBlur}
                        value={
                          (field.value as string | number | undefined) ?? ""
                        }
                        onChange={(e) => field.onChange(e.target.value)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="focusGoalMinutes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gaze time goal</FormLabel>
                    <FormControl>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">15 min</span>
                          <span className="font-medium">{field.value} min</span>
                          <span className="text-muted-foreground">240 min</span>
                        </div>

                        <Slider
                          min={15}
                          max={240}
                          step={15}
                          value={[field.value ?? 60]}
                          onValueChange={(value) => field.onChange(value[0])}
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
            control={form.control}
            name="focusScoreGoal"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Gaze score goal</FormLabel>
                <FormControl>
                  <div className="space-y-4 flex flex-col items-center">

                    {/* ring */}
                    <GoalRingInput value={field.value ?? 85} />

                    {/* slider */}
                    <Slider
                      min={0}
                      max={100}
                      step={1}
                      value={[field.value ?? 85]}
                      onValueChange={(value) => field.onChange(value[0])}
                      className="w-full"
                    />

                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
            </div>

            <div className="flex justify-end">
              <Button type="submit" className="cursor-pointer" variant="secondary" size="sm" disabled={saving}>
                {saving ? "Updating..." : "Update Goals"}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}