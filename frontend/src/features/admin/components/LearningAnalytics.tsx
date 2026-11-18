import { AnalyticsInfo } from './AnalyticsInfo'
import { useState } from 'react'
import { BarChart3, BookOpen, Target } from 'lucide-react'
import { ModuleActivityCharts } from './ModuleActivityCharts'
import type { PerformanceSummary } from '@/features/performance/types'
import { EMPTY_RATE, GO_SCR_TARGET, KPIS, MODULES, getModuleRate, moduleTarget, type Rate, type Status } from '../utils/kpiCatalogue'
import { soMetricRate, soStatus } from '../utils/objectiveEvaluation'
import { formatMetricValue, kpiEvidence, metricTargetStatus, type KpiKey } from '@/features/performance/utils/performanceKpis'

const verdict = (value: Status) => value === 'met' ? 'Met' : value === 'miss' ? 'Not met' : 'No evidence'

function ObjectiveProgress({ label, statuses }: { label: string; statuses: Status[] }) {
  const met = statuses.filter(s => s === 'met').length
  const missing = statuses.filter(s => s === 'none').length
  return <div className="la-objective-progress">
    <div><span>{label}</span><strong>{met} / {statuses.length}</strong></div>
    <progress aria-label={`${label} met`} value={met} max={statuses.length} />
    <small>{statuses.length - met - missing} not met · {missing} with no evidence</small>
  </div>
}

export function LearningAnalytics({ summary, objectives }: { summary: PerformanceSummary; objectives: Record<string, Rate> }) {
  const [key, setKey] = useState<KpiKey>('scr')
  const [moduleFilter, setModuleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const kpi = KPIS.find(k => k.key === key)!
  const modules = MODULES.map(meta => ({ meta, data: summary.modules.find(m => m.number === meta.num) }))
  const rows = modules.flatMap(({ meta, data }) => meta.sos.map(so => ({
    so, module: meta.num, data: { module: data, objectives }, status: soStatus(so, { module: data, objectives }),
  })))
  const general = modules.map(({ data }) => metricTargetStatus(data?.scr ?? EMPTY_RATE, GO_SCR_TARGET, true))
  const specific = rows.map(row => row.status)
  const totalMet = [...general, ...specific].filter(s => s === 'met').length
  const chart = modules.map(({ meta, data }) => ({
    meta, rate: data ? getModuleRate(data, key) : EMPTY_RATE, target: moduleTarget(key, meta.num),
    applicable: key !== 'rta' || meta.num >= 3,
  }))
  const maximum = kpi.pct ? 100 : Math.max(4, ...chart.map(row => row.rate.value ?? 0))
  const filtered = rows.filter(row => (moduleFilter === 'all' || row.module === Number(moduleFilter)) && (statusFilter === 'all' || row.status === statusFilter))

  return <div className="la-grid">
    <section className="la-panel la-comparison" aria-labelledby="la-comparison-title">
      <div className="la-heading"><div><h2 id="la-comparison-title"><BarChart3 aria-hidden="true" />Compare Module Performance</h2><p>See how each module compares with its target.</p></div>
        <label className="la-select">KPI<select value={key} onChange={e => setKey(e.target.value as KpiKey)}>{KPIS.map(k => <option key={k.key} value={k.key}>{k.abbr} — {k.name}</option>)}</select></label>
      </div>
      <AnalyticsInfo title="About trends"><div className="la-chart-toolbar"><div className="la-view-toggle" aria-label="KPI chart view"><button type="button" aria-pressed="true">By Module</button><button type="button" disabled aria-describedby="la-trend-reason">Trend</button></div><span id="la-trend-reason">Historical KPI snapshots unavailable</span></div></AnalyticsInfo>
      <div className="la-chart" role="group" aria-label={`${kpi.name} by module`}>
        <div className="la-axis"><span>{maximum}{kpi.pct ? '%' : ' retries'}</span><span>{maximum / 2}{kpi.pct ? '%' : ''}</span><span>0</span></div>
        {chart.map(({ meta, rate, target, applicable }) => <div className="la-column" key={meta.num}>
          <div className="la-plot">
            {applicable && <div className="la-target" style={{ bottom: `${target / maximum * 100}%` }}><span>{kpi.up ? '≥' : '≤'}{target}{kpi.pct ? '%' : ''}</span></div>}
            {applicable && rate.value !== null && rate.denominator > 0
              ? <div className="la-bar" style={{ height: `${Math.max(0, rate.value / maximum * 100)}%` }}><strong>{formatMetricValue(rate.value, kpi.pct)}</strong></div>
              : <span className="la-chart-empty">{applicable ? 'No evidence' : 'Not applicable'}</span>}
          </div>
          <strong>Module {meta.num}</strong><span className="la-module-name">{meta.title}</span>
          <AnalyticsInfo title="Evidence"><p>{applicable ? kpiEvidence(key, rate) : 'Transfer is assessed in Modules 3–4'}</p></AnalyticsInfo>
        </div>)}
      </div>
      <p className="la-footnote">Dashed markers show targets. {kpi.up ? 'Higher is better.' : 'Lower is better. Values show average retries.'}</p>
    </section>

    <ModuleActivityCharts activity={summary.module_activity} />

    <section className="la-panel la-lessons" aria-labelledby="la-lessons-title">
      <div className="la-heading"><div><h2 id="la-lessons-title"><BookOpen aria-hidden="true" />Lesson Performance</h2><p>Review lesson results and the targets they need to meet.</p></div></div>
      <div className="la-filters"><label className="la-select">Module<select value={moduleFilter} onChange={e => setModuleFilter(e.target.value)}><option value="all">All modules</option>{MODULES.map(m => <option key={m.num} value={m.num}>Module {m.num}</option>)}</select></label>
        <label className="la-select">Status<select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}><option value="all">All statuses</option><option value="met">Met</option><option value="miss">Not met</option><option value="none">No evidence</option></select></label><span>{filtered.length} of {rows.length} objectives</span></div>
      <p className="la-caption">Every listed target must be met. Open Evidence for contributor counts and measurement scope.</p>
      <div className="la-table-scroll" tabIndex={0} role="region" aria-label="Specific objective results"><table className="la-table"><thead><tr><th>Module</th><th>Lesson / objective</th><th>KPI result / target</th><th>Status</th></tr></thead><tbody>
        {filtered.map(row => <tr key={row.so.id}><td><span className="dk-chip">Module {row.module}</span></td><th scope="row"><small>{row.so.id}</small>{row.so.title}</th><td>{row.so.metrics.map(metric => {
          const rate = soMetricRate(metric, row.so, row.data)
          const meta = KPIS.find(k => k.key === metric.kpi)!
          return <div className="la-result" key={metric.kpi}><div><b title={meta.name}>{meta.abbr}</b><strong>{formatMetricValue(rate.value, meta.pct)}</strong><span>{metric.up ? '≥' : '≤'}{metric.target}{meta.pct ? '%' : ''}</span></div><AnalyticsInfo title="Evidence"><small>{metric.kpi === 'car' ? 'Objective' : 'Module'} scope · {kpiEvidence(metric.kpi, rate)}</small></AnalyticsInfo></div>
        })}</td><td><span className={`la-status is-${row.status}`}>{verdict(row.status)}</span></td></tr>)}
        {!filtered.length && <tr><td colSpan={4}>No objectives match these filters.</td></tr>}
      </tbody></table></div>
    </section>

    <section className="la-panel la-objectives" aria-labelledby="la-objectives-title"><h2 id="la-objectives-title"><Target aria-hidden="true" />Research Objectives Met</h2>
      <div className="la-total"><strong>{totalMet}<span> / {general.length + specific.length}</span></strong><span>Total objectives met</span></div>
      <ObjectiveProgress label="General objectives" statuses={general} /><ObjectiveProgress label="Specific objectives" statuses={specific} />
      <p className="la-footnote">An objective is met only when all its required KPI targets are met. Missing evidence never counts as success.</p>
    </section>
  </div>
}
