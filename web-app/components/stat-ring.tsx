import { cn } from "@/lib/utils"
import { ReactNode } from "react"
import { Card, CardContent } from "./ui/card"

interface StatRingProps {
  label: string
  value: ReactNode
  percent: number
  goal?: ReactNode
  colourClass?: string
}

export function StatRing({
  label,
  value,
  percent,
  colourClass = 'stroke-blue-600',
  goal,
}: StatRingProps) {
  const p = Math.max(0, Math.min(100, percent))
  const r = 34
  const c = 2 * Math.PI * r
  const dash = (p / 100) * c

  return (
        <div className="flex flex-col text-center items-center gap-4">
          {/* Ring */}
          <div className="relative h-35 w-35 shrink-0">
            <svg viewBox="0 0 80 80" className="-rotate-90">
              <circle
                cx="40"
                cy="40"
                r={r}
                strokeWidth="8"
                className="fill-none stroke-muted"
              />
              <circle
                cx="40"
                cy="40"
                r={r}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${dash} ${c - dash}`}
                className={cn('fill-none', colourClass)}
              />
            </svg>

            {/* Center value */}
            <div className="absolute inset-0 flex items-center justify-center text-sm font-semibold">
              {Math.round(p)}%
            </div>
          </div>

          {/* Label + value */}
          <div>
            <div className="text-sm text-muted-foreground">{label}</div>
            <div className="mt-1 text-l font-semibold">{value}</div>
            <div className="text-xs text-muted-foreground">Goal: {goal}</div>
          </div>
        </div>
  )
}