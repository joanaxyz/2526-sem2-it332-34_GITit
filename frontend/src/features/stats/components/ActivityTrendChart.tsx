import { useState } from 'react'

import type { TrendPoint } from '@/features/stats/types'
import { Card, CardContent } from '@/shared/components/Card'

const W = 520
const H = 170
const PAD_X = 8
const PAD_TOP = 14
const PAD_BOTTOM = 22

type SeriesKey = 'commands_run' | 'problems_completed'

const SERIES: { key: SeriesKey; label: string; noun: string }[] = [
  { key: 'commands_run', label: 'Commands run', noun: 'commands' },
  { key: 'problems_completed', label: 'Quests finished', noun: 'quests' },
]

function shortDate(iso: string): string {
  const d = new Date(`${iso}T00:00:00`)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function ActivityTrendChart({ trend }: { trend: TrendPoint[] }) {
  const [active, setActive] = useState<SeriesKey>('commands_run')
  const series = SERIES.find((s) => s.key === active)!

  const values = trend.map((p) => p[active])
  const max = Math.max(...values, 1)
  const n = trend.length

  const x = (i: number) => PAD_X + (i / (n - 1)) * (W - PAD_X * 2)
  const y = (v: number) => PAD_TOP + (1 - v / max) * (H - PAD_TOP - PAD_BOTTOM)

  const line = values.map((v, i) => `${i === 0 ? 'M' : 'L'} ${x(i)} ${y(v)}`).join(' ')
  const area = `${line} L ${x(n - 1)} ${H - PAD_BOTTOM} L ${x(0)} ${H - PAD_BOTTOM} Z`

  const thisWeek = values.slice(-7).reduce((a, b) => a + b, 0)
  const lastWeek = values.slice(-14, -7).reduce((a, b) => a + b, 0)
  const delta = thisWeek - lastWeek
  const trendUp = delta >= 0

  return (
    <Card className="overflow-hidden shadow-none">
      <CardContent className="p-5">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold tracking-tight">Your last 2 weeks</h2>
            <p className="text-xs text-muted-foreground">
              <span className="font-semibold text-aurora-cyan">{thisWeek}</span> {series.noun} this week
              {lastWeek > 0 && (
                <span className={trendUp ? 'text-emerald-400' : 'text-rose-400'}>
                  {' '}
                  {trendUp ? '▲' : '▼'} {Math.abs(delta)} vs last
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-1 rounded-md border border-border bg-card/40 p-0.5">
            {SERIES.map((s) => (
              <button
                key={s.key}
                type="button"
                onClick={() => setActive(s.key)}
                className={`rounded px-2.5 py-1 text-[0.68rem] font-medium transition-colors ${
                  active === s.key ? 'bg-aurora-cyan/15 text-aurora-cyan' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <svg width="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="overflow-visible">
          <defs>
            <linearGradient id="trend-stroke" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#00F5D4" />
              <stop offset="100%" stopColor="#00B4D8" />
            </linearGradient>
            <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00F5D4" stopOpacity="0.28" />
              <stop offset="100%" stopColor="#00B4D8" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Baseline */}
          <line x1={PAD_X} y1={H - PAD_BOTTOM} x2={W - PAD_X} y2={H - PAD_BOTTOM} stroke="rgba(255,255,255,0.08)" strokeWidth={1} />

          <path d={area} fill="url(#trend-fill)" />
          <path d={line} fill="none" stroke="url(#trend-stroke)" strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round" />

          {values.map((v, i) => (
            <circle key={i} cx={x(i)} cy={y(v)} r={v > 0 ? 3 : 0} fill="#00F5D4" style={{ filter: 'drop-shadow(0 0 3px #00F5D4)' }}>
              <title>{`${shortDate(trend[i].date)}: ${v} ${series.noun}`}</title>
            </circle>
          ))}

          {/* x-axis ticks: first, middle, last */}
          {[0, Math.floor((n - 1) / 2), n - 1].map((i) => (
            <text
              key={i}
              x={x(i)}
              y={H - 6}
              textAnchor={i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'}
              className="fill-muted-foreground"
              style={{ fontSize: 9 }}
            >
              {shortDate(trend[i].date)}
            </text>
          ))}
        </svg>
      </CardContent>
    </Card>
  )
}
