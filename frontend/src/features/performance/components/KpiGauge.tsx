import type { RateMetric } from '@/features/performance/types'
import { formatMetricValue } from '@/features/performance/utils/performanceKpis'

type KpiGaugeProps = {
  rate: RateMetric
  target: number
  percent: boolean
  name: string
  compact?: boolean
}

const ARC_PATH = 'M 21.009 78.991 A 41 41 0 1 1 78.991 78.991'

/** Actual readings on a 270-degree scale; the small radial tick marks the goal. */
export function KpiGauge({ rate, target, percent, name, compact = false }: KpiGaugeProps) {
  const measured = rate.value !== null && rate.denominator > 0
  const ceiling = percent ? 100 : Math.max(6, Math.ceil(rate.value ?? 0))
  const reading = measured ? Math.max(0, Math.min(ceiling, rate.value!)) : 0
  const value = measured ? formatMetricValue(rate.value, percent) : '—'
  const angle = (135 + target / ceiling * 270) * Math.PI / 180
  const point = (radius: number) => ({ x: 50 + radius * Math.cos(angle), y: 50 + radius * Math.sin(angle) })
  const inner = point(35)
  const outer = point(47)
  const goal = `${percent ? 'at least' : 'at most'} ${target}${percent ? '%' : ' retries'}`

  return (
    <div
      className={`kpi-gauge${compact ? ' kpi-gauge--compact' : ''}`}
      data-empty={!measured || undefined}
      role={measured ? 'meter' : undefined}
      aria-hidden={measured ? undefined : true}
      aria-label={measured ? name : undefined}
      aria-valuemin={measured ? 0 : undefined}
      aria-valuemax={measured ? ceiling : undefined}
      aria-valuenow={measured ? reading : undefined}
      aria-valuetext={measured ? `${value}${percent ? '' : ' retries'}; goal ${goal}; ${percent ? 'higher' : 'lower'} is better` : undefined}
    >
      <svg viewBox="0 0 100 100" fill="none" aria-hidden="true">
        <path className="kpi-gauge-track" d={ARC_PATH} pathLength="100" />
        {measured && reading > 0 ? <path className="kpi-gauge-fill" d={ARC_PATH} pathLength="100" strokeDasharray={`${reading / ceiling * 100} 100`} /> : null}
        <line className="kpi-gauge-goal" x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y} />
        {measured && reading === 0 ? <circle className="kpi-gauge-zero" cx="21.009" cy="78.991" r="2.7" /> : null}
      </svg>
      <strong className="kpi-gauge-value">{value}</strong>
    </div>
  )
}
