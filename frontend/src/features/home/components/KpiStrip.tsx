import { RotateCcw } from 'lucide-react'

import type { HomeSummary, RateMetric } from '@/features/home/types'
import { RingGauge } from '@/features/stats/components/RingGauge'
import { useCountUp } from '@/features/stats/useCountUp'

const CYAN = '#00F5D4'
const BLUE = '#00B4D8'

type RateKpi = {
  key: string
  label: string
  metric: RateMetric
  unit: string
}

function RateRow({ kpi, index }: { kpi: RateKpi; index: number }) {
  const hasData = kpi.metric.value !== null
  const counted = useCountUp(kpi.metric.value)
  const accent = index % 2 === 0 ? CYAN : BLUE

  return (
    <div
      className="kpi-line animate-fade-in-up"
      style={{ ['--line-accent' as string]: accent, animationDelay: `${index * 45}ms` }}
    >
      <RingGauge value={kpi.metric.value} color={accent} label={kpi.label} showValue={false} size={38} />
      <div className="min-w-0 flex-1">
        <p className="truncate font-mono text-[0.6rem] font-semibold uppercase tracking-[0.14em] text-aurora-blue/80">
          {kpi.label}
        </p>
        <p className="mt-0.5 truncate font-mono text-[0.6rem] text-muted-foreground/85">
          {hasData ? `${kpi.metric.numerator}/${kpi.metric.denominator} ${kpi.unit}` : 'no runs yet'}
        </p>
      </div>
      <p className="kpi-line-value">
        {hasData ? (
          <>
            {Math.round(counted)}
            <span>%</span>
          </>
        ) : (
          '-'
        )}
      </p>
    </div>
  )
}

function RetryRow({ metric, index }: { metric: RateMetric; index: number }) {
  const hasData = metric.value !== null
  return (
    <div
      className="kpi-line animate-fade-in-up"
      style={{ ['--line-accent' as string]: BLUE, animationDelay: `${index * 45}ms` }}
    >
      <span className="kpi-line-icon" aria-hidden="true">
        <RotateCcw className="size-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-mono text-[0.6rem] font-semibold uppercase tracking-[0.14em] text-aurora-blue/80">
          Avg Retries
        </p>
        <p className="mt-0.5 truncate font-mono text-[0.6rem] text-muted-foreground/85">per quest, lower is better</p>
      </div>
      <p className="kpi-line-value">
        {hasData ? (
          <>
            {(metric.value ?? 0).toFixed(1)}
            <span>x</span>
          </>
        ) : (
          '-'
        )}
      </p>
    </div>
  )
}

/** Compact KPI diagnostics for the stats tab. */
export function KpiStrip({ summary }: { summary: HomeSummary }) {
  const k = summary.kpis
  const rates: RateKpi[] = [
    { key: 'car', label: 'Cmd Accuracy', metric: k.car, unit: 'commands' },
    { key: 'scr', label: 'Scenario Clear', metric: k.scr, unit: 'scenarios' },
    { key: 'practice_completion', label: 'Practice Done', metric: k.practice_completion, unit: 'practices' },
    { key: 'hlcr', label: 'Hard Clear', metric: k.hlcr, unit: 'hard quests' },
    { key: 'rta', label: 'Retry Transfer', metric: k.rta, unit: 'retried wins' },
  ]

  return (
    <section className="flex flex-col" aria-label="Performance diagnostics">
      <h3 className="text-[0.95rem] font-bold tracking-tight">Diagnostics</h3>

      <div className="mt-2 grid grid-cols-2 gap-x-8 max-md:grid-cols-1">
        {rates.map((kpi, i) => (
          <RateRow key={kpi.key} kpi={kpi} index={i} />
        ))}
        <RetryRow metric={k.arc} index={rates.length} />
      </div>
    </section>
  )
}
