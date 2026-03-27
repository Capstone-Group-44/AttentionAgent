"use client"
import { saveUserProfile } from "@/lib/api/profile"
import { useAuthUser } from "@/lib/hooks/use-auth-user"
import { useUserProfile } from "@/lib/hooks/use-user-profile"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { updateProfile } from "firebase/auth"

export default function ProfilePage() {
  const form = useForm({
  defaultValues: {
    displayName: "",
    bio: "",
  },
})
const { user } = useAuthUser()

async function onSubmit(values: { displayName: string; bio: string }) {
  if (!user) return

  await saveUserProfile(user.uid, values)

  await updateProfile(user, {
    displayName: values.displayName,
  })
}
const { data } = useUserProfile(user?.uid)

useEffect(() => {
  if (data) {
    form.reset({
      displayName: data.displayName ?? "",
      bio: data.bio ?? "",
    })
  }
}, [data, form])

  return (
  <main className="mx-auto">
    {/* HEADER */}
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">Profile</h1>
      <p className="text-muted-foreground">
        Manage your personal information and profile details.
      </p>
    </div>

    {/* CONTENT */}
    <div className="space-y-6">
      <div className="rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-4">Profile Details</h2>
        <p className="text-sm text-muted-foreground mb-6">
          Update the information shown on your account.
        </p>

        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="max-w-md space-y-4"
        >
          <div>
            <label className="text-sm font-medium">Name</label>
            <input
              {...form.register("displayName")}
              className="w-full mt-1 rounded-md border px-3 py-2"
              placeholder="Your name" 
            />
          </div>

          <div>
            <label className="text-sm font-medium">Bio</label>
            <textarea
              {...form.register("bio")}
              className="w-full mt-1 rounded-md border px-3 py-2"
              placeholder="Tell us about yourself"
              rows={4}
            />
          </div>

          <button
            type="submit"
            className="rounded-md border px-4 py-2 text-sm font-medium"
          >
            Save changes
          </button>
        </form>
      </div>
    </div>
  </main>
)
}