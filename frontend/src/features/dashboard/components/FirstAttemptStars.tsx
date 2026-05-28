import { useEffect, useState } from 'react'
import { Star } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

function useCountUp(target: number, duration = 900): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === 0) { setValue(0); return }
    const startTime = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - startTime) / duration, 1)
      setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [target, duration])
  return value
}

export function FirstAttemptStars({ summary }: { summary: DashboardSummary }) {
  const count = useCountUp(summary.first_attempt_stars)
  const attempted = summary.counts.started
  const stars = summary.first_attempt_stars
  const displaySlots = Math.min(attempted, 10)
  const filledCount = Math.min(stars, displaySlots)

  return (
    <Card className="dash-card-hover" style={{ borderLeft: '2px solid rgba(0,245,212,0.3)' }}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="size-5 text-primary" />
          First-attempt stars
        </CardTitle>
        <CardDescription>
          Awarded only when a completed primary session has no misses or invalid commands.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="number-glow text-4xl font-extrabold text-primary">
          {count}
        </div>
        <p className="mt-1.5 text-xs text-muted-foreground">
          {stars} out of {attempted} sessions — keep it up!
        </p>
        {displaySlots > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {Array.from({ length: displaySlots }, (_, i) => (
              <Star
                key={i}
                className="size-4"
                style={{
                  color: i < filledCount ? '#00F5D4' : 'rgba(100,116,139,0.22)',
                  filter: i < filledCount ? 'drop-shadow(0 0 4px rgba(0,245,212,0.5))' : 'none',
                }}
                fill={i < filledCount ? '#00F5D4' : 'none'}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
