import type { ComponentType, ReactNode } from 'react'
import { Flame, Medal, Sparkles, Star, Swords, TerminalSquare } from 'lucide-react'

import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

type Metric = {
  label: string
  value: number | null
  Icon: ComponentType<{ className?: string }>
  note?: string
  micro?: ReactNode
}

function StarRow({ count }: { count: number }) {
  return (
    <span className="flex gap-0.5" aria-hidden="true">
      {Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          className="size-2.5"
          style={
            i < Math.min(count, 5)
              ? { color: CYAN, fill: CYAN, filter: `drop-shadow(0 0 3px ${CYAN}88)` }
              : { color: 'rgba(255,255,255,0.14)' }
          }
        />
      ))}
    </span>
  )
}

function DotRow({ active }: { active: number }) {
  return (
    <span className="flex gap-1" aria-hidden="true">
      {Array.from({ length: 7 }, (_, i) => (
        <span
          key={i}
          className="size-1.5 rounded-full"
          style={
            i < Math.min(active, 7)
              ? { background: CYAN, boxShadow: `0 0 4px ${CYAN}aa` }
              : { background: 'rgba(255,255,255,0.1)' }
          }
        />
      ))}
    </span>
  )
}

function CommandSparkline({ points }: { points: number[] }) {
  const max = Math.max(...points, 1)
  return (
    <span className="flex h-3.5 items-end gap-[2px]" aria-hidden="true">
      {points.map((v, i) => (
        <span
          key={i}
          className="w-[3px] rounded-sm"
          style={{
            height: `${Math.max(12, (v / max) * 100)}%`,
            background: v > 0 ? BLUE : 'rgba(255,255,255,0.12)',
            opacity: v > 0 ? 0.45 + (v / max) * 0.55 : 1,
          }}
        />
      ))}
    </span>
  )
}

function MetricRow({ metric, index }: { metric: Metric; index: number }) {
  const counted = useCountUp(metric.value)
  const hasData = metric.value !== null
  const accent = index % 2 === 0 ? CYAN : BLUE

  return (
    <div
      className="metric-line animate-fade-in-up"
      style={{ ['--line-accent' as string]: accent, animationDelay: `${index * 45}ms` }}
    >
      <span className="metric-line-icon" aria-hidden="true">
        <metric.Icon className="size-4" />
      </span>
      <div className="min-w-0">
        <p className="truncate font-mono text-[0.62rem] font-semibold uppercase tracking-[0.15em] text-aurora-blue/80">
          {metric.label}
        </p>
        {metric.note && <p className="mt-1 truncate text-xs text-muted-foreground/85">{metric.note}</p>}
      </div>
      <div className="metric-line-micro">{metric.micro}</div>
      <p className="metric-line-value">{hasData ? Math.round(counted).toLocaleString() : '-'}</p>
    </div>
  )
}

/** Secondary milestone metrics as a compact ledger instead of a card grid. */
export function MetricGrid({ summary }: { summary: StatsSummary }) {
  const h = summary.headline
  const commandPoints = summary.activity_trend.slice(-10).map((p) => p.commands_run)

  const metrics: Metric[] = [
    {
      label: 'Perfect clears',
      value: h.perfect_clears,
      Icon: Star,
      note: 'no-retry wins',
      micro: <StarRow count={h.perfect_clears} />,
    },
    {
      label: 'Boss floors',
      value: h.boss_floors.value,
      Icon: Swords,
      note: h.boss_floors.scope,
    },
    {
      label: 'Comebacks',
      value: h.comebacks.value,
      Icon: Sparkles,
      note: h.comebacks.scope,
    },
    {
      label: 'Commands run',
      value: h.commands_run,
      Icon: TerminalSquare,
      note: 'all time',
      micro: commandPoints.length > 0 ? <CommandSparkline points={commandPoints} /> : undefined,
    },
    {
      label: 'Day streak',
      value: h.day_streak,
      Icon: Flame,
      note: 'current rhythm',
      micro: <DotRow active={h.day_streak} />,
    },
    {
      label: 'Longest streak',
      value: h.longest_streak,
      Icon: Medal,
      note: 'personal best',
    },
  ]

  return (
    <section className="flex h-full flex-col" aria-label="Milestones">
      <h3 className="text-[0.95rem] font-bold tracking-tight">Milestones</h3>

      <div className="mt-2 grid">
        {metrics.map((metric, index) => (
          <MetricRow key={metric.label} metric={metric} index={index} />
        ))}
      </div>
    </section>
  )
}
