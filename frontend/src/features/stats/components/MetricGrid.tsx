import type { ComponentType, ReactNode } from 'react'
import { Flame, Medal, Sparkles, Star, Swords, TerminalSquare } from 'lucide-react'

import type { StatsSummary } from '@/features/stats/types'
import { useCountUp } from '@/features/stats/useCountUp'

type Metric = {
  label: string
  value: number | null
  Icon: ComponentType<{ className?: string }>
  color: string
  note?: string
  micro?: ReactNode
}

function StarRow({ count, color }: { count: number; color: string }) {
  return (
    <span className="flex gap-0.5" aria-hidden="true">
      {Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          className="size-2.5"
          style={
            i < Math.min(count, 5)
              ? { color, fill: color, filter: `drop-shadow(0 0 3px ${color}88)` }
              : { color: 'rgba(255,255,255,0.14)' }
          }
        />
      ))}
    </span>
  )
}

function DotRow({ active, color }: { active: number; color: string }) {
  return (
    <span className="flex gap-1" aria-hidden="true">
      {Array.from({ length: 7 }, (_, i) => (
        <span
          key={i}
          className="size-1.5 rounded-full"
          style={
            i < Math.min(active, 7)
              ? { background: color, boxShadow: `0 0 4px ${color}aa` }
              : { background: 'rgba(255,255,255,0.1)' }
          }
        />
      ))}
    </span>
  )
}

function CommandSparkline({ points, color }: { points: number[]; color: string }) {
  const max = Math.max(...points, 1)
  return (
    <span className="flex h-3.5 items-end gap-[2px]" aria-hidden="true">
      {points.map((v, i) => (
        <span
          key={i}
          className="w-[3px] rounded-sm"
          style={{
            height: `${Math.max(12, (v / max) * 100)}%`,
            background: v > 0 ? color : 'rgba(255,255,255,0.12)',
            opacity: v > 0 ? 0.45 + (v / max) * 0.55 : 1,
          }}
        />
      ))}
    </span>
  )
}

function MetricTile({ metric, index }: { metric: Metric; index: number }) {
  const hasData = metric.value !== null
  const counted = useCountUp(metric.value)
  return (
    <div
      className="stat-tile group animate-fade-in-up p-3.5"
      style={{ ['--tile-accent' as string]: metric.color, animationDelay: `${index * 55}ms` }}
    >
      <div className="relative z-[1] flex items-start justify-between gap-2">
        <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.12em] text-aurora-blue/80">
          {metric.label}
        </p>
        <span
          className="game-chip size-7 transition-transform duration-200 group-hover:scale-110"
          style={{ borderColor: `${metric.color}55` }}
        >
          <metric.Icon className="size-3.5" />
        </span>
      </div>
      {hasData ? (
        <p
          className="relative z-[1] mt-1.5 text-[1.7rem] font-extrabold leading-none tracking-tight"
          style={{ color: metric.color, textShadow: `0 0 20px ${metric.color}55` }}
        >
          {Math.round(counted)}
        </p>
      ) : (
        <p className="relative z-[1] mt-1.5 text-[1.7rem] font-extrabold leading-none text-muted-foreground/40">—</p>
      )}
      <div className="relative z-[1] mt-2 flex min-h-[0.9rem] items-center justify-between gap-2">
        {metric.micro ?? <span />}
        {metric.note && (
          <p className="truncate text-right font-mono text-[0.58rem] text-muted-foreground/65">{metric.note}</p>
        )}
      </div>
    </div>
  )
}

/**
 * Secondary milestone metrics with per-metric accent colors and embedded
 * micro-visuals (star rows, streak dots, command sparkline).
 */
export function MetricGrid({ summary }: { summary: StatsSummary }) {
  const h = summary.headline
  const commandPoints = summary.activity_trend.slice(-10).map((p) => p.commands_run)

  const metrics: Metric[] = [
    {
      label: 'Perfect Clears',
      value: h.perfect_clears,
      Icon: Star,
      color: '#FBBF24',
      note: 'no-retry wins',
      micro: <StarRow count={h.perfect_clears} color="#FBBF24" />,
    },
    {
      label: 'Boss Floors',
      value: h.boss_floors.value,
      Icon: Swords,
      color: '#A78BFA',
      note: h.boss_floors.scope,
    },
    {
      label: 'Comebacks',
      value: h.comebacks.value,
      Icon: Sparkles,
      color: '#F472B6',
      note: h.comebacks.scope,
    },
    {
      label: 'Commands Run',
      value: h.commands_run,
      Icon: TerminalSquare,
      color: '#7DD3FC',
      note: 'all time',
      micro: commandPoints.length > 0 ? <CommandSparkline points={commandPoints} color="#7DD3FC" /> : undefined,
    },
    {
      label: 'Day Streak',
      value: h.day_streak,
      Icon: Flame,
      color: '#FB923C',
      micro: <DotRow active={h.day_streak} color="#FB923C" />,
    },
    {
      label: 'Longest Streak',
      value: h.longest_streak,
      Icon: Medal,
      color: '#34D399',
      note: 'personal best',
    },
  ]

  return (
    <section aria-label="Milestone metrics" className="grid grid-cols-3 gap-3 max-md:grid-cols-2">
      {metrics.map((metric, index) => (
        <MetricTile key={metric.label} metric={metric} index={index} />
      ))}
    </section>
  )
}
