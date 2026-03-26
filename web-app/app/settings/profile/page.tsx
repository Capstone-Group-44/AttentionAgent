export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <div className="rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-4">Profile</h2>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-muted-foreground">Name</label>
            <input
              className="w-full mt-1 rounded-md border px-3 py-2"
              placeholder="Your name"
            />
          </div>

          <div>
            <label className="text-sm text-muted-foreground">Bio</label>
            <textarea
              className="w-full mt-1 rounded-md border px-3 py-2"
              placeholder="Tell us about yourself"
            />
          </div>
        </div>
      </div>
    </div>
  )
}