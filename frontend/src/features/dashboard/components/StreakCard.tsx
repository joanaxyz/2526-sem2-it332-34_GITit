import { useEffect, useState } from 'react'
import { Flame } from 'lucide-react'

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

function getDaysGrid(streakCurrent: number, lastCompletedOn: string | null) {
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const today = new Date()
  const lastDate = lastCompletedOn ? new Date(lastCompletedOn) : null
  if (lastDate) lastDate.setHours(0, 0, 0, 0)

  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today)
    d.setDate(today.getDate() - (6 - i))
    d.setHours(0, 0, 0, 0)
    let active = false
    if (lastDate && streakCurrent > 0) {
      const diffDays = Math.round((lastDate.getTime() - d.getTime()) / 86400000)
      active = diffDays >= 0 && diffDays < streakCurrent
    }
    return { day: dayNames[d.getDay()].slice(0, 3), active }
  })
}

export function StreakCard({ summary }: { summary: DashboardSummary }) {
  const current = useCountUp(summary.streak.current)
  const longest = useCountUp(summary.streak.longest)
  const days = getDaysGrid(summary.streak.current, summary.streak.last_completed_on)

  return (
    <Card className="dash-card-hover" style={{ borderLeft: '2px solid rgba(0,245,212,0.3)' }}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="flame-glow size-5 text-primary" />
          Streak
        </CardTitle>
        <CardDescription>Updated on the first completed scenario session per day.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="number-glow text-4xl font-extrabold text-primary">
          {current}
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <span
            className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
            style={{
              background: 'rgba(0,245,212,0.1)',
              border: '1px solid rgba(0,245,212,0.35)',
              color: '#00F5D4',
              boxShadow: '0 0 8px rgba(0,245,212,0.2)',
            }}
          >
            Longest {longest}
          </span>
          <span
            className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
            style={{
              background: 'rgba(0,180,216,0.08)',
              border: '1px solid rgba(0,180,216,0.3)',
              color: '#00B4D8',
            }}
          >
            {summary.streak.last_completed_on ?? 'No completion yet'}
          </span>
        </div>

        {/* 7-day activity grid */}
        <div className="mt-4">
          <div className="flex gap-1.5">
            {days.map(({ day, active }, i) => (
              <div key={i} className="flex flex-col items-center gap-1">
                <div
                  className="size-7 rounded-sm"
                  style={{
                    background: active ? 'rgba(0,245,212,0.28)' : 'rgba(0,180,216,0.07)',
                    border: active ? '1px solid rgba(0,245,212,0.5)' : '1px solid rgba(0,180,216,0.12)',
                    boxShadow: active ? '0 0 6px rgba(0,245,212,0.22)' : 'none',
                    transition: 'background 0.2s ease',
                  }}
                />
                <span className="text-[9px] text-muted-foreground/45">{day}</span>
              </div>
            ))}
          </div>
          <p className="mt-1.5 text-[10px] text-muted-foreground/35">based on current streak</p>
        </div>
      </CardContent>
    </Card>
  )
}
