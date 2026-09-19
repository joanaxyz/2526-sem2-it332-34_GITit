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
