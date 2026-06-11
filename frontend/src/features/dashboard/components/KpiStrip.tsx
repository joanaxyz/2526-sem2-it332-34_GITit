import { RotateCcw } from 'lucide-react'

import type { DashboardSummary, RateMetric } from '@/features/dashboard/types'
import { RingGauge } from '@/features/stats/components/RingGauge'
import { useCountUp } from '@/features/stats/useCountUp'

type RateKpi = {
  key: string
  label: string
  metric: RateMetric
  color: string
  unit: string
}

function RateCard({ kpi, index }: { kpi: RateKpi; index: number }) {
  const hasData = kpi.metric.value !== null
  const counted = useCountUp(kpi.metric.value)
  return (
    <div
      className="stat-tile animate-fade-in-up flex items-center gap-3 p-3.5"
      style={{ ['--tile-accent' as string]: kpi.color, animationDelay: `${index * 50}ms` }}
    >
      <div className="relative z-[1]">
        <RingGauge value={kpi.metric.value} color={kpi.color} label={kpi.label} showValue={false} size={42} />
      </div>
      <div className="relative z-[1] min-w-0">
        <p className="truncate font-mono text-[0.6rem] font-semibold uppercase tracking-[0.12em] text-aurora-blue/80">
          {kpi.label}
        </p>
        {hasData ? (
          <>
            <p
              className="mt-0.5 text-[1.45rem] font-extrabold leading-none tracking-tight"
              style={{ color: kpi.color, textShadow: `0 0 18px ${kpi.color}55` }}
            >
              {Math.round(counted)}
              <span className="text-sm font-bold">%</span>
            </p>
            <p className="mt-0.5 truncate font-mono text-[0.6rem] text-muted-foreground/70">
              {kpi.metric.numerator}/{kpi.metric.denominator} {kpi.unit}
            </p>
          </>
        ) : (
          <>
            <p className="mt-0.5 text-[1.45rem] font-extrabold leading-none text-muted-foreground/40">—</p>
            <p className="mt-0.5 font-mono text-[0.6rem] text-muted-foreground/50">no runs yet</p>
          </>
        )}
      </div>
    </div>
  )
}

/** Average retry count — a count metric, so it gets a numeric badge instead of a ring. */
function RetryCard({ metric, index }: { metric: RateMetric; index: number }) {
  const hasData = metric.value !== null
  const color = '#FB923C'
  return (
    <div
      className="stat-tile animate-fade-in-up flex items-center gap-3 p-3.5"
      style={{ ['--tile-accent' as string]: color, animationDelay: `${index * 50}ms` }}
    >
      <span
        className="relative z-[1] grid size-[42px] shrink-0 place-items-center rounded-full"
        style={{
          border: `1.5px solid ${color}66`,
          background: `radial-gradient(circle at 35% 30%, ${color}2e, rgba(4,16,32,0.7) 75%)`,
          boxShadow: `inset 0 0 8px ${color}22, 0 0 12px ${color}1f`,
        }}
        aria-hidden="true"
      >
        <RotateCcw className="size-4" style={{ color }} />
      </span>
      <div className="relative z-[1] min-w-0">
        <p className="truncate font-mono text-[0.6rem] font-semibold uppercase tracking-[0.12em] text-aurora-blue/80">
          Avg Retries
        </p>
        {hasData ? (
          <>
            <p
              className="mt-0.5 text-[1.45rem] font-extrabold leading-none tracking-tight"
              style={{ color, textShadow: `0 0 18px ${color}55` }}
            >
              {(metric.value ?? 0).toFixed(1)}
              <span className="text-sm font-bold">×</span>
            </p>
            <p className="mt-0.5 truncate font-mono text-[0.6rem] text-muted-foreground/70">per quest · lower is better</p>
          </>
        ) : (
          <>
            <p className="mt-0.5 text-[1.45rem] font-extrabold leading-none text-muted-foreground/40">—</p>
            <p className="mt-0.5 font-mono text-[0.6rem] text-muted-foreground/50">no runs yet</p>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * Tracker-style KPI strip: six compact cards, each with an embedded
 * micro-visual (ring gauge for rates, numeric badge for the retry count).
 */
export function KpiStrip({ summary }: { summary: DashboardSummary }) {
  const k = summary.kpis
  const rates: RateKpi[] = [
    { key: 'car', label: 'Cmd Accuracy', metric: k.car, color: '#7DD3FC', unit: 'commands' },
    { key: 'scr', label: 'Scenario Clear', metric: k.scr, color: '#00F5D4', unit: 'scenarios' },
    { key: 'practice_completion', label: 'Practice Done', metric: k.practice_completion, color: '#34D399', unit: 'practices' },
    { key: 'hlcr', label: 'Hard Clear', metric: k.hlcr, color: '#A78BFA', unit: 'hard quests' },
    { key: 'rta', label: 'Retry Transfer', metric: k.rta, color: '#FBBF24', unit: 'retried wins' },
  ]

  return (
    <section aria-label="Key performance indicators" className="grid grid-cols-6 gap-3 max-2xl:grid-cols-3 max-md:grid-cols-2">
      {rates.map((kpi, i) => (
        <RateCard key={kpi.key} kpi={kpi} index={i} />
      ))}
      <RetryCard metric={k.arc} index={rates.length} />
    </section>
  )
}
