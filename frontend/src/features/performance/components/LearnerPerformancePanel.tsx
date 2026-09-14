import { useQuery } from '@tanstack/react-query'
import { AlertCircle, BarChart3, RefreshCw } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import { performanceApi } from '@/features/performance/api/performanceApi'
import type { PerformanceSummary, RateMetric } from '@/features/performance/types'
import { queryKeys } from '@/shared/api/queryKeys'

// Learner-facing Overview shows outcome metrics only. The diagnostic measures
// (command processability, retry transfer, average retries) are staff signals
// and live on the admin analytics console instead.
type LearnerMetric = 'scr' | 'hlcr'

const LEARNER_METRICS: Record<LearnerMetric, { label: string; description: string }> = {
  scr: {
    label: 'Scenario completion',
    description: 'How often you finish a Runebound scenario after starting it.',
  },
  hlcr: {
    label: 'Hard completion',
    description: 'How often you finish a hard Runebound scenario after starting it.',
  },
}

function learnerMetric(value: string | null): LearnerMetric {
  return value === 'hlcr' ? 'hlcr' : 'scr'
}

function formatPercent(metric: RateMetric) {
  return metric.value === null ? '--' : `${Math.round(metric.value)}%`
}

function evidenceLabel(metric: RateMetric) {
  if (!metric.denominator) return 'No attempts yet'
  return `${metric.numerator} of ${metric.denominator} attempts`
}

function PanelShell({ children }: { children: React.ReactNode }) {
  return (
    <section
      className="home-performance-insights"
      aria-labelledby="performance-insights-title"
      data-onboarding="overview-performance"
    >
      {children}
    </section>
  )
}

function ModuleBreakdown({
  modules,
  metric,
  metricLabel,
}: {
  modules: PerformanceSummary['modules']
  metric: LearnerMetric
  metricLabel: string
}) {
  return (
    <div className="home-performance-chart" aria-label={`${metricLabel} by module`}>
      <div className="home-performance-chart-head">
        <span>By module</span>
        <span>Completion</span>
      </div>
      {modules.map((module) => {
        const value = module[metric]
        return (
          <div className="home-performance-row" key={module.number}>
            <span title={module.title}>
              <b>{module.number}</b>
              {module.title}
            </span>
            <div
              className="home-performance-meter"
              aria-label={`Module ${module.number} ${module.title}: ${formatPercent(value)}, ${evidenceLabel(value)}`}
            >
              <i style={{ width: `${Math.max(0, Math.min(100, value.value ?? 0))}%` }} />
            </div>
            <strong>{formatPercent(value)}</strong>
          </div>
        )
      })}
    </div>
  )
}

export function LearnerPerformancePanel() {
  const [searchParams, setSearchParams] = useSearchParams()
  const selected = learnerMetric(searchParams.get('metric'))
  const performance = useQuery({
    queryKey: queryKeys.performanceSummary,
    queryFn: performanceApi.summary,
    staleTime: 60 * 1000,
  })

  function selectMetric(metric: LearnerMetric) {
    setSearchParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (metric === 'scr') next.delete('metric')
        else next.set('metric', metric)
        return next
      },
      { replace: true },
    )
  }

  if (performance.isPending) {
    return (
      <section className="home-performance-insights is-loading" aria-label="Loading performance">
        <span />
        <span />
        <span />
      </section>
    )
  }

  // Data wins over a failed background refetch: a stale panel beats replacing
  // a working one with an error.
  if (!performance.data) {
    return (
      <section className="home-performance-insights home-performance-error" aria-label="Performance">
        <AlertCircle aria-hidden="true" />
        <div>
          <strong>Performance insights are unavailable</strong>
          <p>Your progress is safe. This panel just could not load.</p>
        </div>
        <button type="button" onClick={() => void performance.refetch()} disabled={performance.isFetching}>
          <RefreshCw aria-hidden="true" />
          {performance.isFetching ? 'Retrying' : 'Try again'}
        </button>
      </section>
    )
  }

  const data = performance.data
  const detail = LEARNER_METRICS[selected]
  const headline = data.kpis[selected]

  return (
    <PanelShell>
      <header className="home-performance-head">
        <div>
          <span className="home-performance-label">
            <BarChart3 aria-hidden="true" />
            Your performance
          </span>
          <h2 id="performance-insights-title">See what is improving</h2>
        </div>
        <div className="home-performance-toggle" role="radiogroup" aria-label="Performance metric">
          {(Object.keys(LEARNER_METRICS) as LearnerMetric[]).map((metric) => (
            <label key={metric} className={selected === metric ? 'is-selected' : ''}>
              <input
                type="radio"
                name="performance-metric"
                value={metric}
                checked={selected === metric}
                onChange={() => selectMetric(metric)}
              />
              {LEARNER_METRICS[metric].label}
            </label>
          ))}
        </div>
      </header>

      <div className="home-performance-summary">
        <div>
          <strong>{formatPercent(headline)}</strong>
          <span>{detail.label}</span>
          <small>{evidenceLabel(headline)}</small>
        </div>
        <p>{detail.description}</p>
      </div>

      <ModuleBreakdown modules={data.modules} metric={selected} metricLabel={detail.label} />
    </PanelShell>
  )
}
