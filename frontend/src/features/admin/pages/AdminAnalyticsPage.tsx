import { useQuery } from '@tanstack/react-query'
import { Activity, Command, RotateCcw } from 'lucide-react'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading, StatTile } from '@/features/admin/components/adminUi'
import type { PerformanceModule, RateMetric } from '@/features/performance/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

// Diagnostic Runebound metrics are staff-only: they describe simulator and
// retry behaviour, not learner outcomes, so they never appear in the player UI.
type DiagnosticMetric = 'rtr' | 'arc'

function formatPercent(metric: RateMetric) {
  return metric.value === null ? '--' : `${Math.round(metric.value)}%`
}

function formatScalar(metric: RateMetric) {
  return metric.value === null ? '--' : metric.value.toFixed(2)
}

function evidenceLabel(metric: RateMetric, noun: string) {
  if (!metric.denominator) return `No ${noun} yet`
  return `${metric.numerator} / ${metric.denominator} ${noun}`
}

type RateMetricLike = { value: number | null; numerator: number; denominator: number }

const ALL_KPI_META = [
  { key: 'scr',  label: 'SCR',  full: 'Scenario Completion Rate',   target: 80,  higherIsBetter: true,  unit: '%',  format: 'percent', modules: '1–4' },
  { key: 'car',  label: 'CAR',  full: 'Command Accuracy Rate',       target: 70,  higherIsBetter: true,  unit: '%',  format: 'percent', modules: '1–4' },
  { key: 'hlcr', label: 'HLCR', full: 'Hard-Level Completion Rate',  target: 70,  higherIsBetter: true,  unit: '%',  format: 'percent', modules: '1–3 (≥65% M4)' },
  { key: 'arc',  label: 'ARC',  full: 'Average Retry Count',         target: 2,   higherIsBetter: false, unit: '',   format: 'decimal', modules: '1–3 (≤3 M4)' },
  { key: 'rtr',  label: 'RTR',  full: 'Retry Transfer Rate',         target: 65,  higherIsBetter: true,  unit: '%',  format: 'percent', modules: '3–4' },
]

function fmtRate(value: number | null, format: string): string {
  if (value === null) return '--'
  return format === 'percent' ? `${value}%` : value.toFixed(2)
}

function kpiStatus(value: number | null, target: number, higherIsBetter: boolean): 'met' | 'missed' | 'empty' {
  if (value === null) return 'empty'
  return (higherIsBetter ? value >= target : value <= target) ? 'met' : 'missed'
}

function StatusCell({ rate, target, higherIsBetter, format }: {
  rate: RateMetricLike | undefined
  target: number
  higherIsBetter: boolean
  format: string
}) {
  if (!rate) return <td className="px-3 py-2 text-center text-muted-foreground text-xs">--</td>
  const status = kpiStatus(rate.value, target, higherIsBetter)
  const color = status === 'met' ? 'text-green-400 font-bold' : status === 'missed' ? 'text-red-400 font-bold' : 'text-muted-foreground'
  const bg = status === 'met' ? 'bg-green-400/10' : status === 'missed' ? 'bg-red-400/10' : ''
  return (
    <td className={`px-3 py-2 text-center text-xs ${color} ${bg}`}>
      {fmtRate(rate.value, format)}
      {rate.denominator > 0 && (
        <span className="ml-1 text-muted-foreground font-normal">({rate.denominator})</span>
      )}
    </td>
  )
}

function KpiSummaryTable({ diagnostics, passRate, totalRuns, passedRuns }: {
  diagnostics: { kpis: { scr?: RateMetricLike; car: RateMetricLike; hlcr: RateMetricLike; rtr: RateMetricLike; arc: RateMetricLike }; modules: PerformanceModule[] }
  passRate: number
  totalRuns: number
  passedRuns: number
}) {
  const scrOverall: RateMetricLike = {
    value: totalRuns > 0 ? passRate : null,
    numerator: passedRuns,
    denominator: totalRuns,
  }

  const overallByKey: Record<string, RateMetricLike> = {
    scr: scrOverall,
    car: diagnostics.kpis.car,
    hlcr: diagnostics.kpis.hlcr,
    arc: diagnostics.kpis.arc,
    rtr: diagnostics.kpis.rtr,
  }

  return (
    <div className="admin-table-scroll">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase text-muted-foreground">
            <th className="px-3 py-2 font-semibold">KPI</th>
            <th className="px-3 py-2 font-semibold">Description</th>
            <th className="px-3 py-2 font-semibold text-center">Target</th>
            <th className="px-3 py-2 font-semibold text-center">Overall</th>
            {diagnostics.modules.map((m) => (
              <th key={m.number} className="px-3 py-2 font-semibold text-center">M{m.number}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ALL_KPI_META.map((meta) => {
            const overall = overallByKey[meta.key]
            return (
              <tr key={meta.key} className="border-b border-border/40">
                <td className="px-3 py-2">
                  <span className="font-mono font-bold text-foreground">{meta.label}</span>
                  <span className="ml-2 text-xs text-muted-foreground">{meta.modules}</span>
                </td>
                <td className="px-3 py-2 text-muted-foreground">{meta.full}</td>
                <td className="px-3 py-2 text-center text-xs text-muted-foreground">
                  {meta.higherIsBetter ? '≥' : '≤'}{meta.target}{meta.unit}
                </td>
                <StatusCell rate={overall} target={meta.target} higherIsBetter={meta.higherIsBetter} format={meta.format} />
                {diagnostics.modules.map((mod) => {
                  const modRate = meta.key === 'scr' ? mod.scr
                    : meta.key === 'car' ? undefined
                    : meta.key === 'hlcr' ? mod.hlcr
                    : meta.key === 'arc' ? mod.arc
                    : meta.key === 'rtr' ? mod.rtr
                    : undefined
                  return (
                    <StatusCell key={mod.number} rate={modRate} target={meta.target} higherIsBetter={meta.higherIsBetter} format={meta.format} />
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
      <p className="mt-2 text-xs text-muted-foreground px-3 pb-2">
        Green = target met · Red = target missed · (n) = sessions/attempts · -- = no data
      </p>
    </div>
  )
}

function ModuleRows({
  modules,
  metric,
  scalar = false,
}: {
  modules: PerformanceModule[]
  metric: DiagnosticMetric
  scalar?: boolean
}) {
  // Averages have no natural ceiling, so scalar rows are scaled against the
  // largest value in this set. Rate rows stay on their true 0-100 scale.
  const ceiling = Math.max(...modules.map((module) => module[metric].value ?? 0), 1)

  return (
    <div className="admin-diagnostic-rows">
      {modules.map((module) => {
        const value = module[metric]
        const display = scalar ? formatScalar(value) : formatPercent(value)
        const width = scalar ? ((value.value ?? 0) / ceiling) * 100 : value.value ?? 0
        return (
          <div className="admin-diagnostic-row" key={module.number}>
            <span title={module.title}>{module.number}</span>
            <div
              className={`admin-diagnostic-meter${value.value === null ? ' is-empty' : ''}`}
              aria-label={`Module ${module.number} ${module.title}: ${display}, ${evidenceLabel(value, 'attempts')}`}
            >
              <i style={{ width: `${Math.max(0, Math.min(100, width))}%` }} />
            </div>
            <strong>{display}</strong>
          </div>
        )
      })}
    </div>
  )
}

export function AdminAnalyticsPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: queryKeys.adminAnalytics,
    queryFn: adminApi.analytics,
  })

  if (isPending) return <LoadingScreen label="Loading analytics" />
  if (isError || !data) {
    return <ErrorState title="Could not load analytics" description="Try again shortly." />
  }

  const passRate = data.runs.total > 0 ? Math.round((data.runs.passed / data.runs.total) * 100) : 0
  const diagnostics = data.runebound_performance

  return (
    <div className="admin-analytics-page">
      <PageHeading
        title="Progress & Analytics"
        description="How learners move through the curriculum and where the Runebound experience needs attention."
      />

      <section className="admin-summary-grid" aria-label="Learning summary">
        <StatTile
          label="All runs"
          value={data.runs.total}
          hint={`${data.runs.adventure.total} adventure - ${data.runs.challenge.total} challenge`}
        />
        <StatTile label="Pass rate" value={`${passRate}%`} hint={`${data.runs.passed} passed`} />
        <StatTile label="Active learners" value={data.active_learners_30d} hint="last 30 days" />
        <StatTile
          label="Level completions"
          value={data.completions.total}
          hint={`${data.completions.adventure} adventure - ${data.completions.challenge} challenge`}
        />
      </section>

      <section className="admin-section" aria-labelledby="runebound-diagnostics-title">
        <header className="admin-section-head">
          <div>
            <span className="admin-eyebrow">
              <Activity aria-hidden="true" />
              Runebound diagnostics
            </span>
            <h2 id="runebound-diagnostics-title">Technical signals across all learners</h2>
          </div>
          <p className="admin-section-note">Modules 1-4 - replay runs excluded</p>
        </header>

        <div className="admin-diagnostic-grid">
          <article>
            <header className="admin-diagnostic-head">
              <Command aria-hidden="true" />
              <span>Command processability</span>
            </header>
            <strong className="admin-diagnostic-value">{formatPercent(diagnostics.kpis.car)}</strong>
            <p>Submitted commands the simulator could process.</p>
            <small>{evidenceLabel(diagnostics.kpis.car, 'commands')} - aggregate only</small>
          </article>

          <article>
            <header className="admin-diagnostic-head">
              <RotateCcw aria-hidden="true" />
              <span>Retry transfer</span>
            </header>
            <strong className="admin-diagnostic-value">{formatPercent(diagnostics.kpis.rtr)}</strong>
            <p>Retry runs that end in a successful completion.</p>
            <small>{evidenceLabel(diagnostics.kpis.rtr, 'retry attempts')}</small>
            <ModuleRows modules={diagnostics.modules} metric="rtr" />
          </article>

          <article>
            <header className="admin-diagnostic-head">
              <Activity aria-hidden="true" />
              <span>Average retries</span>
            </header>
            <strong className="admin-diagnostic-value">{formatScalar(diagnostics.kpis.arc)}</strong>
            <p>Retries accumulated per completed session.</p>
            <small>{evidenceLabel(diagnostics.kpis.arc, 'completed sessions')} - relative scale</small>
            <ModuleRows modules={diagnostics.modules} metric="arc" scalar />
          </article>
        </div>
      </section>

      <section className="admin-section" aria-labelledby="kpi-summary-title">
        <header className="admin-section-head">
          <div>
            <h2 id="kpi-summary-title">KPI Summary — All Learners</h2>
          </div>
          <p className="admin-section-note">Runebound Turret · Modules 1–4</p>
        </header>
        <KpiSummaryTable diagnostics={diagnostics} passRate={passRate} totalRuns={data.runs.total} passedRuns={data.runs.passed} />
      </section>

      <div className="admin-section admin-analytics-split">
        <section className="admin-data-panel">
          <h2>Runs by status</h2>
          <ul className="admin-status-list">
            {Object.entries(data.runs.by_status).map(([status, count]) => (
              <li key={status}>
                <span>{status}</span>
                <strong>{count}</strong>
              </li>
            ))}
            {Object.keys(data.runs.by_status).length === 0 ? (
              <li className="is-empty">No runs yet.</li>
            ) : null}
          </ul>
        </section>

        <section className="admin-data-panel">
          <h2>Completions</h2>
          <ul className="admin-status-list">
            <li>
              <span>Adventure levels</span>
              <strong>{data.completions.adventure}</strong>
            </li>
            <li>
              <span>Challenge levels</span>
              <strong>{data.completions.challenge}</strong>
            </li>
          </ul>
        </section>
      </div>

      <section className="admin-section admin-story-table" aria-labelledby="story-analytics-title">
        <header className="admin-section-head">
          <div>
            <h2 id="story-analytics-title">Per story</h2>
          </div>
          <p className="admin-section-note">{data.per_story.length} tracked</p>
        </header>
        <div className="admin-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Story</th>
                <th>Runs</th>
                <th>Adventure</th>
                <th>Challenge</th>
                <th>Passed</th>
              </tr>
            </thead>
            <tbody>
              {data.per_story.map((story) => (
                <tr key={story.slug}>
                  <th scope="row">{story.title}</th>
                  <td>{story.runs}</td>
                  <td>{story.adventure_runs}</td>
                  <td>{story.challenge_runs}</td>
                  <td>{story.passed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
