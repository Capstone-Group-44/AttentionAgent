import { Card, CardContent } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import { ReactNode } from "react"

interface StatCardProps {
  label: string
  value: ReactNode
  icon?: LucideIcon
}

export function StatCard({ label, value, icon: Icon }: StatCardProps) {
  return (
    <Card className="py-0">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className="flex items-center justify-center rounded-full bg-blue-100 text-blue-600 ring-4 ring-blue-100">
              <Icon size={20} strokeWidth={1.75} />
            </div>
          )}

          <div>
            <div className="text-sm text-muted-foreground">{label}</div>
            <div className="mt-1 text-2xl font-semibold">{value}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
