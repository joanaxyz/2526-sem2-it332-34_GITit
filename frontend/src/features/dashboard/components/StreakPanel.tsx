import { Flame, Trophy } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { useCountUp } from '@/features/stats/useCountUp'
import { GamePanel } from '@/shared/components/GamePanel'

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
    return { day: dayNames[d.getDay()], active }
  })
}

/** Streak panel: flame motif, big current-streak count, 7-day activity grid. */
export function StreakPanel({ summary }: { summary: DashboardSummary }) {
  const current = useCountUp(summary.streak.current)
  const longest = useCountUp(summary.streak.longest)
  const days = getDaysGrid(summary.streak.current, summary.streak.last_completed_on)
  const alive = summary.streak.current > 0

  return (
    <GamePanel className="p-5">
      <div className="relative z-[1] flex items-center justify-between gap-2">
        <h3 className="font-mono text-[0.66rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
          Streak
        </h3>
        <span
          className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 font-mono text-[0.62rem] font-bold uppercase tracking-[0.08em]"
          style={{
            color: '#FBBF24',
            border: '1px solid rgba(251,191,36,0.35)',
            background: 'rgba(251,191,36,0.08)',
          }}
        >
          <Trophy aria-hidden="true" className="size-3" />
          Best {Math.round(longest)}
        </span>
      </div>

      <div className="relative z-[1] mt-3 flex items-end gap-3">
        <span
          className="game-chip size-12 shrink-0"
          style={{ borderColor: 'rgba(251,146,60,0.4)' }}
        >
          <Flame
            aria-hidden="true"
            className={`size-6 ${alive ? 'flame-glow' : ''}`}
            style={{ color: alive ? '#FB923C' : 'rgba(148,163,184,0.5)' }}
          />
        </span>
        <span
          className={`text-5xl font-extrabold leading-none ${alive ? 'number-glow text-primary' : 'text-muted-foreground/40'}`}
        >
          {Math.round(current)}
        </span>
        <span className="pb-1 text-sm font-semibold text-muted-foreground">
          day{summary.streak.current === 1 ? '' : 's'}
        </span>
      </div>

      <div className="relative z-[1] mt-4">
        <div className="flex gap-1.5">
          {days.map(({ day, active }, i) => (
            <div key={i} className="flex flex-1 flex-col items-center gap-1">
              <div
                className="h-7 w-full rounded-md"
                style={{
                  background: active ? 'rgba(0,245,212,0.28)' : 'rgba(0,180,216,0.07)',
                  border: active ? '1px solid rgba(0,245,212,0.5)' : '1px solid rgba(0,180,216,0.12)',
                  boxShadow: active ? '0 0 6px rgba(0,245,212,0.22)' : 'none',
                }}
              />
              <span className="font-mono text-[9px] uppercase text-muted-foreground/45">{day}</span>
            </div>
          ))}
        </div>
        <p className="mt-2 font-mono text-[0.6rem] text-muted-foreground/45">
          {summary.streak.last_completed_on
            ? `last clear ${summary.streak.last_completed_on}`
            : 'first completed session each day keeps it alive'}
        </p>
      </div>
    </GamePanel>
  )
}
