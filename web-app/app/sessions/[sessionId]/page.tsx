type PageProps = {
  params: { sessionId: string }
}

export default function SessionDetailsPage({ params }: PageProps) {
  return (
    <div className="p-6 space-y-2">
      <h1 className="font-semibold">Session Details</h1>
    </div>
  )
}
