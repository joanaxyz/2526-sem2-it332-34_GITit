import { useId, useRef, type KeyboardEvent } from 'react'
import { Check, ChevronDown, GitBranch, RotateCcw, Swords, Target, Terminal } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { KpiGauge } from './KpiGauge'

import {
  EMPTY_RATE, KPIS, SUPPLEMENTARY_KPI, formatKpi, kpiEvidence, metricTargetStatus,
  type KpiKey, type Status,
} from '@/features/performance/utils/performanceKpis'
import { GO_SCR_TARGET, MODULES, moduleTarget } from '@/features/performance/utils/learningObjectives'
import type { PerformanceSummary, RateMetric } from '@/features/performance/types'

const KPI_ICONS = { scr: Target, car: Terminal, hlcr: Swords, arc: RotateCcw, rta: GitBranch }

const STATUS_TEXT: Record<Status, string> = {
  met: 'Target met', miss: 'Keep practicing', none: 'Not measured yet',
}

function StatusBadge({ status }: { status: Status }) {
  return <span className="objective-status" data-state={status}>
    {status === 'met' ? <Check aria-hidden="true" /> : null}{STATUS_TEXT[status]}
  </span>
}

function MetricReading({ metric, rate, target, compact = false }: { metric: KpiKey; rate: RateMetric; target: number; compact?: boolean }) {
  const definition = KPIS.find((item) => item.key === metric)!
  const status = metricTargetStatus(rate, target, definition.up)
  const Icon = KPI_ICONS[metric]
  const name = 'longName' in definition ? definition.longName : definition.name
  const heading = <div className="objective-metric-heading">
    <span className="objective-metric-icon" aria-hidden="true"><Icon /></span><span>{name}</span>
  </div>
  const goal = <span className="objective-metric-target">Goal {definition.up ? '≥' : '≤'}{target}{definition.pct ? '%' : ''}</span>
  const gauge = <KpiGauge rate={rate} target={target} percent={definition.pct} name={name} compact={compact} />

  return (
    <div className={`objective-metric objective-metric--${compact ? 'compact' : 'overview'}`} data-state={status}>
      {compact ? <>
        <div className="objective-metric-copy">
          {heading}
          <div className="objective-metric-goal-line">{goal}{!definition.up ? <span>Lower is better</span> : null}</div>
          <small>{kpiEvidence(metric, rate)}</small>
        </div>
        {gauge}
      </> : <>
        {heading}
        {gauge}
        <div className="objective-metric-goal-line">{goal}<StatusBadge status={status} /></div>
        <p className="objective-metric-direction">{!definition.up ? 'Lower is better' : ' '}</p>
        <small>{kpiEvidence(metric, rate)}</small>
      </>}
    </div>
  )
}

/** All modules and objectives share one authenticated, server-calculated response. */
export function LearnerPerformanceInstrument({ data }: { data: PerformanceSummary }) {
  const location = useLocation()
  const navigate = useNavigate()
  const tabId = useId()
  const tabRefs = useRef<Record<number, HTMLButtonElement | null>>({})
  const selected = Number(location.hash.match(/^#learning-module-([1-4])$/)?.[1] ?? 1)
  const selectedResults = data.modules.find((item) => item.number === selected)
  const recovery = selectedResults?.retry_success_rate ?? EMPTY_RATE

  function selectModule(number: number) {
    void navigate({ pathname: location.pathname, search: location.search, hash: `#learning-module-${number}` }, { replace: true, preventScrollReset: true })
  }

  function onTabKeyDown(event: KeyboardEvent<HTMLButtonElement>, number: number) {
    const next = event.key === 'ArrowRight' ? number % 4 + 1
      : event.key === 'ArrowLeft' ? (number + 2) % 4 + 1
        : event.key === 'Home' ? 1 : event.key === 'End' ? 4 : null
    if (next === null) return
    event.preventDefault()
    selectModule(next)
    tabRefs.current[next]?.focus()
  }

  return (
    <div className="learning-objectives-record">
      <div className="objective-module-tabs" role="tablist" aria-label="Learning modules">
        {MODULES.map((module) => <button
          key={module.num} type="button" role="tab" id={`${tabId}-module-${module.num}`}
          aria-selected={selected === module.num} aria-controls={`learning-module-${module.num}`}
          tabIndex={selected === module.num ? 0 : -1}
          ref={(element) => { tabRefs.current[module.num] = element }}
          onClick={() => selectModule(module.num)} onKeyDown={(event) => onTabKeyDown(event, module.num)}
        ><span className="objective-tab-index" aria-hidden="true">0{module.num}</span>Module {module.num}</button>)}
      </div>
      {MODULES.map((module) => {
        const results = data.modules.find((item) => item.number === module.num)
        const rateFor = (key: KpiKey) => results?.[key] ?? EMPTY_RATE
        const metrics = KPIS.filter((item) => item.key !== 'rta' || module.num >= 3)
        return (
          <section className="learning-module" role="tabpanel" tabIndex={0} hidden={selected !== module.num}
            id={`learning-module-${module.num}`} key={module.num} aria-labelledby={`${tabId}-module-${module.num}`}>
            {selected === module.num ? <>
            <header className="learning-module-heading">
              <div className="learning-module-eyebrow"><span className="learning-module-number">Module 0{module.num}</span><span>{module.sos.length} specific objectives</span></div>
              <h3 id={`learning-module-title-${module.num}`}>{module.title}</h3>
              <details className="learning-module-objective" key={module.num}>
                <summary>General objective <ChevronDown aria-hidden="true" /></summary>
                <p>{module.go}</p>
              </details>
            </header>
            <div className="objective-module-kpis" data-count={metrics.length} role="group" aria-label={`Module ${module.num} KPIs`}>
              {metrics.map((metric) => <MetricReading key={metric.key} metric={metric.key} rate={rateFor(metric.key)} target={metric.key === 'scr' ? GO_SCR_TARGET : moduleTarget(metric.key, module.num)} />)}
            </div>
            <div className="specific-objectives-heading"><h4>Specific objectives</h4><span>Performance by learning objective</span></div>
            <ol className="specific-objectives" aria-label={`Module ${module.num} specific objectives`}>
              {module.sos.map((objective) => {
                const readings = objective.metrics.map((metric) => ({
                  ...metric,
                  rate: metric.kpi === 'car' ? data.objectives?.[objective.id] ?? EMPTY_RATE : rateFor(metric.kpi),
                }))
                const statuses = readings.map((item) => metricTargetStatus(item.rate, item.target, item.up))
                const status: Status = statuses.includes('none') ? 'none' : statuses.every((item) => item === 'met') ? 'met' : 'miss'
                return (
                  <li key={objective.id} className="specific-objective" data-state={status} aria-label={`${objective.id} ${objective.title}`}>
                    <div className="specific-objective-identity">
                      <span className="specific-objective-code">{objective.id}</span>
                      <div className="specific-objective-title">
                        <h5>{objective.title}</h5>
                        <StatusBadge status={status} />
                        {readings.length > 1 ? <small>Both targets required · module results</small> : null}
                      </div>
                    </div>
                    <div className="specific-objective-metrics" data-dual={readings.length > 1 || undefined}>
                      {readings.map((item) => <MetricReading key={item.kpi} metric={item.kpi} rate={item.rate} target={item.target} compact />)}
                    </div>
                  </li>
                )
              })}
            </ol>
            </> : null}
          </section>
        )
      })}
      <details className="performance-calculation">
        <summary>How these KPIs are measured</summary>
        <p>Arcane Spire practice in Modules 1–4, across all time. Replay runs are excluded. The activity range above does not change these results.</p>
        <p>Scenario Completion Rate measures each general objective. Command Accuracy Rate uses each specific objective’s mapped scenarios; the module summary combines the module’s assessments. Hard-Level Completion Rate, Average Retry Count, and Retry Transfer Accuracy use module results.</p>
        {KPIS.map((metric) => <div key={metric.key}>
          <h4>{'longName' in metric ? metric.longName : metric.name} ({metric.abbr})</h4>
          <p>{metric.explanation}</p>
          <p>{metric.formula}</p>
          <p>{metric.why}</p>
        </div>)}
        <p>{data.samples.car_missing} mastered tiers lack validated command evidence and remain unscored.</p>
        <p>{data.samples.in_progress_tiers} opened tiers are in progress and not counted yet.</p>
      </details>
      {selected >= 3 ? <details className="objective-transfer-checkpoints performance-calculation">
        <summary>Available transfer checkpoints · Modules 3–4</summary>
        <p>Modules 3–4 · {data.samples.transfer_pending} pending · {data.samples.transfer_missing} mastered tiers without eligible transfer evidence</p>
        {data.transfers.length > 0 ? <ul aria-label="Available transfer checkpoints">
          {data.transfers.map((point) => <li key={point.tier_id}>
            <Link to={point.run_id ? `/adventure-tier-runs/${point.run_id}` : `/adventure-level-tiers/${point.tier_id}/runs?transfer=1`}>
              {point.run_id ? 'Resume' : 'Start'} transfer checkpoint: {point.title}
            </Link>
          </li>)}
        </ul> : <p>{KPIS.find((metric) => metric.key === 'rta')!.emptyHint}</p>}
      </details> : null}
      <details className="performance-calculation" key={selected}>
        <summary>Module {selected} retry recovery · supplementary</summary>
        <p>{formatKpi('retry_success_rate', recovery)} · {kpiEvidence('retry_success_rate', recovery)}</p>
        <p>{SUPPLEMENTARY_KPI.explanation}</p>
        <p>{SUPPLEMENTARY_KPI.formula}</p>
        <p>For context · no target</p>
      </details>
    </div>
  )
}
