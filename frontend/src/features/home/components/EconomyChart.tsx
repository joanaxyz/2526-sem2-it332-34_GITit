import { useMemo, useState } from 'react'
import { Area, AreaChart, CartesianGrid, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import type { TrendPoint } from '@/features/stats/types'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'
const MONO = 'JetBrains Mono, ui-monospace, monospace'

type RangeKey = '7d' | '14d'

const RANGES: { key: RangeKey; label: string; days: number }[] = [
  { key: '7d', label: '1 week', days: 7 },
  { key: '14d', label: '2 weeks', days: 14 },
]

function weekday(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { weekday: 'long' })
}

function shortDate(iso: string): string {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

type TooltipPayload = { value: number; dataKey: string; payload: TrendPoint }

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload
  return (
    <div className="rounded-lg border border-aurora-cyan/40 bg-[#06121f]/95 px-3 py-2 shadow-[0_0_18px_rgba(0,245,212,0.18)] backdrop-blur">
      <p className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.1em] text-aurora-blue/85">
        {shortDate(point.date)}
      </p>
      <p className="mt-0.5 text-xs" style={{ color: CYAN }}>
        <span className="font-mono font-bold">{point.commands_run}</span> commands
      </p>
      <p className="text-xs" style={{ color: BLUE }}>
        <span className="font-mono font-bold">{point.quests_completed}</span> quests
      </p>
    </div>
  )
}

/**
 * "Tokens Economy"-style dual-series chart sitting open on the page —
 * title + range pills + legend up top, the aurora area chart below.
 * No panel chrome; the chart itself is the surface.
 */
export function EconomyChart({ trend }: { trend: TrendPoint[] }) {
  const [range, setRange] = useState<RangeKey>('7d')
  const days = RANGES.find((r) => r.key === range)!.days
  const data = useMemo(() => trend.slice(-days), [trend, days])

  const peak = useMemo(() => {
    if (data.length === 0) return null
    return data.reduce((best, p) => (p.commands_run > best.commands_run ? p : best))
  }, [data])

  const hasData = data.some((p) => p.commands_run > 0 || p.quests_completed > 0)

  return (
    <section className="flex flex-col" aria-label="Activity economy">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <h3 className="text-[0.95rem] font-bold tracking-tight">Activity Economy</h3>
        <div className="flex items-center gap-4 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.06em] text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <span className="size-2 rounded-full" style={{ background: CYAN, boxShadow: `0 0 6px ${CYAN}` }} />
            Commands Run
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="size-2 rounded-full" style={{ background: BLUE, boxShadow: `0 0 6px ${BLUE}` }} />
            Quests Finished
          </span>
        </div>
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

      {!hasData ? (
        <div className="grid place-items-center" style={{ height: 250 }}>
          <p className="text-xs text-muted-foreground/85">No activity yet — your first commands will chart here.</p>
        </div>
      ) : (
      <div className="relative" style={{ height: 250 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 12, bottom: 4, left: -16 }}>
            <defs>
              <linearGradient id="economy-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={CYAN} stopOpacity={0.34} />
                <stop offset="100%" stopColor={CYAN} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="date"
              tickFormatter={range === '7d' ? weekday : shortDate}
              tick={{ fill: 'rgba(148,163,184,0.85)', fontSize: 9.5, fontFamily: MONO }}
              tickLine={false}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              interval="preserveStartEnd"
              minTickGap={18}
            />
            <YAxis
              allowDecimals={false}
              width={34}
              tick={{ fill: 'rgba(148,163,184,0.8)', fontSize: 9.5, fontFamily: MONO }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'rgba(0,245,212,0.3)', strokeWidth: 1 }} />
            <Area
              type="monotone"
              dataKey="commands_run"
              stroke={CYAN}
              strokeWidth={2.5}
              fill="url(#economy-fill)"
              dot={false}
              activeDot={{ r: 4.5, fill: CYAN, stroke: '#06121f', strokeWidth: 2 }}
              isAnimationActive
              animationDuration={700}
            />
            <Area
              type="monotone"
              dataKey="quests_completed"
              stroke={BLUE}
              strokeWidth={2}
              fill="transparent"
              dot={false}
              activeDot={{ r: 4, fill: BLUE, stroke: '#06121f', strokeWidth: 2 }}
              isAnimationActive
              animationDuration={700}
            />
            {peak && peak.commands_run > 0 && (
              <ReferenceDot
                x={peak.date}
                y={peak.commands_run}
                r={5}
                fill={CYAN}
                stroke="#06121f"
                strokeWidth={2.5}
                style={{ filter: `drop-shadow(0 0 6px ${CYAN})` }}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
      )}

      {/* Accessible fallback for the chart */}
      <p className="sr-only">
        Activity over the selected range:{' '}
        {data.map((p) => `${shortDate(p.date)}: ${p.commands_run} commands, ${p.quests_completed} quests`).join('; ')}
      </p>
    </section>
  )
}
