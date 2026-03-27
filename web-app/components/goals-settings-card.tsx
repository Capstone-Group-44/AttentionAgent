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

const formSchema = z.object({
  sessionsGoal: z.coerce.number().int().min(1, "Must be at least 1"),
  focusGoalMinutes: z.coerce.number().int().min(1, "Must be at least 1"),
  focusScoreGoal: z.coerce
    .number()
    .int()
    .min(1, "Must be at least 1")
    .max(100, "Must be 100 or less"),
})

type FormInput = z.input<typeof formSchema>
type FormOutput = z.output<typeof formSchema>

export function GoalsSettingsCard() {
  const [saving, setSaving] = useState(false)

  const { user } = useAuthUser()
  const { goals, loading } = useUserGoals(user?.uid)

  const form = useForm<FormInput, unknown, FormOutput>({
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

  async function onSubmit(values: FormOutput) {
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
            <div className="grid gap-4 sm:grid-cols-3">
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
                    <FormLabel>Gaze time goal (minutes)</FormLabel>
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
                name="focusScoreGoal"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Gaze score goal</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        max={100}
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