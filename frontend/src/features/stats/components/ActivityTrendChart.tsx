import { useState } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { TrendPoint } from '@/features/stats/types'
import { GamePanel } from '@/shared/components/GamePanel'

type SeriesKey = 'commands_run' | 'problems_completed'

const SERIES: { key: SeriesKey; label: string; noun: string }[] = [
  { key: 'commands_run', label: 'Commands run', noun: 'commands' },
  { key: 'problems_completed', label: 'Quests finished', noun: 'quests' },
]

const MONO = 'JetBrains Mono, ui-monospace, monospace'

function shortDate(iso: string): string {
  const d = new Date(`${iso}T00:00:00`)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

type TooltipPayload = { value: number; payload: TrendPoint }

function ChartTooltip({ active, payload, noun }: { active?: boolean; payload?: TooltipPayload[]; noun: string }) {
  if (!active || !payload?.length) return null
  const point = payload[0]
  return (
    <div className="rounded-lg border border-aurora-cyan/40 bg-[#06121f]/95 px-3 py-2 shadow-[0_0_18px_rgba(0,245,212,0.18)] backdrop-blur">
      <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.1em] text-aurora-blue/85">
        {shortDate(point.payload.date)}
      </p>
      <p className="mt-0.5 text-sm text-aurora-cyan">
        <span className="font-mono font-bold">{point.value}</span>{' '}
        <span className="text-xs text-muted-foreground">{noun}</span>
      </p>
    </div>
  )
}

export function ActivityTrendChart({ trend }: { trend: TrendPoint[] }) {
  const [active, setActive] = useState<SeriesKey>('commands_run')
  const series = SERIES.find((s) => s.key === active)!

  const values = trend.map((p) => p[active])
  const thisWeek = values.slice(-7).reduce((a, b) => a + b, 0)
  const lastWeek = values.slice(-14, -7).reduce((a, b) => a + b, 0)
  const delta = thisWeek - lastWeek
  const trendUp = delta >= 0

  return (
    <GamePanel className="flex flex-col p-5">
      <div className="relative z-[1] mb-3 flex items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
            Activity · Last 14 Days
          </p>
          <p className="mt-1.5 text-xs text-muted-foreground">
            <span className="font-mono font-bold text-aurora-cyan">{thisWeek}</span> {series.noun} this week
            {lastWeek > 0 && (
              <span className={`font-mono font-semibold ${trendUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                {' '}
                {trendUp ? '▲' : '▼'} {Math.abs(delta)} vs last
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-1 rounded-lg border border-border bg-card/40 p-0.5">
          {SERIES.map((s) => (
            <button
              key={s.key}
              type="button"
              onClick={() => setActive(s.key)}
              aria-pressed={active === s.key}
              className={`rounded-md px-2.5 py-1 font-mono text-[0.62rem] font-semibold uppercase tracking-[0.04em] transition-colors ${
                active === s.key
                  ? 'bg-aurora-cyan/15 text-aurora-cyan shadow-[inset_0_0_0_1px_rgba(0,245,212,0.3)]'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="relative z-[1]" style={{ height: 210 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trend} margin={{ top: 8, right: 8, bottom: 4, left: -18 }}>
            <defs>
              <linearGradient id="trend-stroke" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#00F5D4" />
                <stop offset="100%" stopColor="#00B4D8" />
              </linearGradient>
              <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00F5D4" stopOpacity={0.32} />
                <stop offset="100%" stopColor="#00B4D8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="date"
              tickFormatter={shortDate}
              tick={{ fill: 'rgba(148,163,184,0.7)', fontSize: 9.5, fontFamily: MONO }}
              tickLine={false}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              interval="preserveStartEnd"
              minTickGap={28}
            />
            <YAxis
              allowDecimals={false}
              width={34}
              tick={{ fill: 'rgba(148,163,184,0.6)', fontSize: 9.5, fontFamily: MONO }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              content={<ChartTooltip noun={series.noun} />}
              cursor={{ stroke: 'rgba(0,245,212,0.3)', strokeWidth: 1 }}
            />
            <Area
              type="monotone"
              dataKey={active}
              stroke="url(#trend-stroke)"
              strokeWidth={2.5}
              fill="url(#trend-fill)"
              dot={false}
              activeDot={{ r: 4, fill: '#00F5D4', stroke: '#06121f', strokeWidth: 2 }}
              isAnimationActive
              animationDuration={700}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Accessible fallback for the chart */}
      <p className="sr-only">
        Activity over the last two weeks: {thisWeek} {series.noun} this week, {lastWeek} the week before.
      </p>
    </GamePanel>
  )
}
