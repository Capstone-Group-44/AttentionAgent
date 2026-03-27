"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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

export function SetGoalsDialog() {
  const [open, setOpen] = useState(false)
  const [saving, setSaving] = useState(false)

  const { user } = useAuthUser()
  const { goals } = useUserGoals(user?.uid)

  const form = useForm<FormInput, unknown, FormOutput>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sessionsGoal: goals.sessionsGoal,
      focusGoalMinutes: Math.floor(goals.focusGoalSeconds / 60),
      focusScoreGoal: goals.focusScoreGoal,
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

      setOpen(false)
    } catch (error) {
      console.error("Failed to save goals:", error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Set Goals</Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Set Daily Goals</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                        value={(field.value as string | number | undefined) ?? ""}
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
                        value={(field.value as string | number | undefined) ?? ""}
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
                  <FormLabel>Average gaze score goal</FormLabel>
                  <FormControl>
                    <Input
                        type="number"
                        min={1}
                        max={100}
                        name={field.name}
                        ref={field.ref}
                        onBlur={field.onBlur}
                        value={(field.value as string | number | undefined) ?? ""}
                        onChange={(e) => field.onChange(e.target.value)}
                        />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={saving}>
              {saving ? "Saving..." : "Save Goals"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}