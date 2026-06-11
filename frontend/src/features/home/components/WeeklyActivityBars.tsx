import { useMemo, useState } from 'react'

import type { TrendPoint } from '@/features/stats/types'

type RangeKey = '7d' | '14d'

const RANGES: { key: RangeKey; label: string; days: number }[] = [
  { key: '7d', label: '1 week', days: 7 },
  { key: '14d', label: '2 weeks', days: 14 },
]

function dayLabel(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { weekday: 'short' })
}

function isToday(iso: string): boolean {
  const d = new Date(`${iso}T00:00:00`)
  const now = new Date()
  return (
    d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()
  )
}

/**
 * "Your Activity"-style thermometer columns sitting open on the page:
 * one glowing pill track per day, filled by commands run, with today's
 * column highlighted in a lit capsule.
 */
export function WeeklyActivityBars({ trend }: { trend: TrendPoint[] }) {
  const [range, setRange] = useState<RangeKey>('7d')
  const days = RANGES.find((r) => r.key === range)!.days
  const data = useMemo(() => trend.slice(-days), [trend, days])
  const max = Math.max(...data.map((p) => p.commands_run), 1)

  return (
    <section className="flex flex-col" aria-label="Daily activity">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="text-[0.95rem] font-bold tracking-tight">Your Activity</h3>
      </div>

      <div className="mb-5 flex gap-1.5" role="group" aria-label="Time range">
        {RANGES.map((r) => (
          <button
            key={r.key}
            type="button"
            className="hub-pill"
            aria-pressed={range === r.key}
            onClick={() => setRange(r.key)}
          >
            {r.label}
          </button>
        ))}
      </div>

      {data.length > 0 ? (
        <div
          className="flex flex-1 items-stretch justify-between gap-1.5"
          style={{ minHeight: 250 }}
          role="img"
          aria-label={`Commands run per day: ${data
            .map((p) => `${dayLabel(p.date)} ${p.commands_run}`)
            .join(', ')}`}
        >
          {data.map((point) => {
            const pct = Math.round((point.commands_run / max) * 100)
            return (
              <div
                key={point.date}
                className="activity-col"
                data-today={isToday(point.date)}
                title={`${dayLabel(point.date)} — ${point.commands_run} commands, ${point.quests_completed} quests`}
              >
                <div className="activity-track">
                  <div
                    className="activity-fill"
                    data-zero={point.commands_run === 0}
                    style={{ height: point.commands_run === 0 ? '6%' : `${Math.max(pct, 8)}%` }}
                  />
                </div>
                <span className="activity-day">{dayLabel(point.date)}</span>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="grid flex-1 place-items-center" style={{ minHeight: 250 }}>
          <p className="text-xs text-muted-foreground/85">No sessions yet — play a day to light a bar.</p>
        </div>
      )}
    </section>
  )
}
