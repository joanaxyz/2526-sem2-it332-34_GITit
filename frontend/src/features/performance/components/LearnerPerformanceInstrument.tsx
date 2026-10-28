import { useId, useRef, useState, type CSSProperties, type KeyboardEvent } from 'react'
import { Check, ChevronDown } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import {
  EMPTY_RATE, KPIS, SUPPLEMENTARY_KPI, formatKpi, kpiEvidence, metricTargetStatus,
  type KpiKey, type Status,
} from '@/features/performance/utils/performanceKpis'
import { GO_SCR_TARGET, MODULES, moduleTarget } from '@/features/performance/utils/learningObjectives'
import type { PerformanceSummary, RateMetric } from '@/features/performance/types'

type ObjectiveStatus = Status | 'partial'
const STATUS_TEXT: Record<ObjectiveStatus, string> = {
  met: 'Target met', miss: 'Keep practicing', none: 'Not measured yet', partial: 'Incomplete evidence',
}

function metricName(key: KpiKey) {
  const definition = KPIS.find((item) => item.key === key)!
  return 'longName' in definition ? definition.longName : definition.name
}

function StatusBadge({ status }: { status: ObjectiveStatus }) {
  return <span className="objective-status" data-state={status}>
    {status === 'met' ? <Check aria-hidden="true" /> : null}{STATUS_TEXT[status]}
  </span>
}

function Goal({ metric, target }: { metric: KpiKey; target: number }) {
  const definition = KPIS.find((item) => item.key === metric)!
  return <span className="objective-metric-target">Goal {definition.up ? '≥' : '≤'}{target}{definition.pct ? '%' : ''}</span>
}

/** Geometry only. Values and goal status always come from the supplied KPI. */
function MeasurementRail({ metric, rate, target, compact = false, scaleMax }: {
  metric: KpiKey; rate: RateMetric; target: number; compact?: boolean; scaleMax?: number
}) {
  const measured = rate.value !== null && rate.denominator > 0
  const count = metric === 'arc'
  const ceiling = count ? scaleMax ?? Math.max(6, Math.ceil(rate.value ?? 0), target) : 100
  const style = {
    '--rail-reading': `${Math.max(0, Math.min(100, (rate.value ?? 0) / ceiling * 100))}%`,
    '--rail-goal': `${target / ceiling * 100}%`,
  } as CSSProperties
  return <div className={`measurement-rail${compact ? ' measurement-rail--compact' : ''}`} data-count={count || undefined} data-empty={!measured || undefined} style={style} aria-hidden="true">
    <span className="measurement-rail-scale">
      <i className="measurement-rail-tick" /><i className="measurement-rail-tick" /><i className="measurement-rail-tick" />
      {measured && !count ? <i className="measurement-rail-fill" /> : null}
      <i className="measurement-rail-goal" />
      {measured ? <i className="measurement-rail-reading" /> : null}
    </span>
    {!compact ? <span className="measurement-rail-labels"><span>0</span><span>{ceiling}{count ? ' retries' : '%'}</span></span> : null}
  </div>
}

function MetricReading({ metric, rate, target, overall = false }: {
  metric: KpiKey; rate: RateMetric; target: number; overall?: boolean
}) {
  const definition = KPIS.find((item) => item.key === metric)!
  const status = metricTargetStatus(rate, target, definition.up)
  return <div className={`objective-metric objective-metric--${overall ? 'overall' : 'module'}`} data-state={status}>
    <div className="objective-metric-heading"><span className="objective-metric-abbr" aria-hidden="true">{definition.abbr}</span><span>{metricName(metric)}</span></div>
    <strong className="objective-metric-value">{formatKpi(metric, rate)}</strong>
    <MeasurementRail metric={metric} rate={rate} target={target} compact={!overall} />
    <div className="objective-metric-foot"><Goal metric={metric} target={target} /><StatusBadge status={status} /></div>
    {metric === 'arc' ? <span className="objective-metric-direction">Lower is better</span> : null}
    {overall && metric === 'rta' ? <span className="objective-metric-direction">Modules 3–4</span> : null}
  </div>
}

function MetricEvidence({ rates, label }: { rates: { key: KpiKey; rate: RateMetric }[]; label: string }) {
  return <details className="record-evidence">
    <summary>{label}</summary>
    <dl>{rates.map(({ key, rate }) => <div key={key}>
      <dt>{metricName(key)}</dt><dd>{kpiEvidence(key, rate)}</dd>
    </div>)}</dl>
  </details>
}

/** One authenticated response supplies every reading; tabs only change the view. */
export function LearnerPerformanceInstrument({ data }: { data: PerformanceSummary }) {
  const location = useLocation()
  const navigate = useNavigate()
  const id = useId()
  const tabRefs = useRef<Record<number, HTMLButtonElement | null>>({})
  const [comparison, setComparison] = useState<KpiKey>('scr')
  const selected = Number(location.hash.match(/^#learning-module-([1-4])$/)?.[1] ?? 1)
  const selectedResults = data.modules.find((item) => item.number === selected)
  const recovery = selectedResults?.retry_success_rate ?? EMPTY_RATE
  const comparisonCeiling = Math.max(6, ...MODULES.map((module) =>
    Math.ceil(data.modules.find((item) => item.number === module.num)?.arc.value ?? 0),
  ))

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
      <section className="record-overall" aria-labelledby={`${id}-overall`}>
        <div className="record-section-heading">
          <h3 id={`${id}-overall`}>Across all modules</h3>
          <span>Mastery KPIs · Modules 1–4</span>
        </div>
        <div className="record-overall-readings" role="group" aria-label="Overall KPIs">
          {KPIS.map((metric) => <MetricReading key={metric.key} metric={metric.key} rate={data.kpis[metric.key]} target={metric.target} overall />)}
        </div>
        <MetricEvidence rates={KPIS.map(({ key }) => ({ key, rate: data.kpis[key] }))} label="Overall evidence" />
      </section>

      <section className="record-comparison" aria-labelledby={`${id}-comparison`}>
        <div className="record-section-heading record-comparison-heading">
          <div><h3 id={`${id}-comparison`}>Compare modules</h3><p>Choose a module to explore its objectives.</p></div>
          <label className="record-comparison-control" htmlFor={`${id}-measure`}>
            <span>Compare by</span>
            <select id={`${id}-measure`} value={comparison} onChange={(event) => setComparison(event.target.value as KpiKey)}>
              {KPIS.map((metric) => <option value={metric.key} key={metric.key}>{metricName(metric.key)}</option>)}
            </select>
          </label>
        </div>
        {comparison === 'arc' ? <p className="record-comparison-direction">Average retries before mastery · lower is better</p> : null}
        <div className="objective-module-tabs" role="tablist" aria-label="Learning modules">
          {MODULES.map((module) => {
            const rate = data.modules.find((item) => item.number === module.num)?.[comparison] ?? EMPTY_RATE
            const applicable = comparison !== 'rta' || module.num >= 3
            const status = metricTargetStatus(rate, moduleTarget(comparison, module.num), KPIS.find((item) => item.key === comparison)!.up)
            return <button
              key={module.num} type="button" role="tab" id={`${id}-module-${module.num}`}
              aria-label={`Module ${module.num}`} aria-describedby={`${id}-comparison-${module.num}`}
              aria-selected={selected === module.num} aria-controls={`learning-module-${module.num}`}
              tabIndex={selected === module.num ? 0 : -1}
              ref={(element) => { tabRefs.current[module.num] = element }}
              onClick={() => selectModule(module.num)} onKeyDown={(event) => onTabKeyDown(event, module.num)}
            >
              <span className="objective-tab-number" aria-hidden="true">0{module.num}</span>
              <span className="objective-tab-title">{module.title}</span>
              <span className="objective-tab-result" id={`${id}-comparison-${module.num}`}>
                <span className="sr-only">{metricName(comparison)}: </span>
                <strong>{applicable ? formatKpi(comparison, rate) : '—'}</strong>
                <span>{applicable ? STATUS_TEXT[status] : 'Not applicable'}</span>
              </span>
              {applicable ? <MeasurementRail metric={comparison} rate={rate} target={moduleTarget(comparison, module.num)} scaleMax={comparisonCeiling} compact /> : <span className="measurement-rail measurement-rail--unavailable" aria-hidden="true" />}
            </button>
          })}
        </div>
      </section>

      {MODULES.map((module) => {
        const results = data.modules.find((item) => item.number === module.num)
        const rateFor = (key: KpiKey) => results?.[key] ?? EMPTY_RATE
        const metrics = KPIS.filter((item) => item.key !== 'rta' || module.num >= 3)
        return (
          <section className="learning-module" role="tabpanel" tabIndex={0} hidden={selected !== module.num}
            id={`learning-module-${module.num}`} key={module.num} aria-labelledby={`${id}-module-${module.num}`}>
            {selected === module.num ? <>
              <header className="learning-module-heading">
                <span className="learning-module-mark" aria-hidden="true">0{module.num}</span>
                <div className="learning-module-heading-copy">
                  <div className="learning-module-context"><span>Module {module.num}</span><span>{module.sos.length} specific objectives</span></div>
                  <h3>{module.title}</h3>
                  <details className="learning-module-objective">
                    <summary>General objective <ChevronDown aria-hidden="true" /></summary>
                    <p>{module.go}</p>
                  </details>
                </div>
              </header>
              <div className="objective-module-kpis" role="group" aria-label={`Module ${module.num} KPIs`}>
                {metrics.map((metric) => <MetricReading key={metric.key} metric={metric.key} rate={rateFor(metric.key)} target={metric.key === 'scr' ? GO_SCR_TARGET : moduleTarget(metric.key, module.num)} />)}
              </div>
              <MetricEvidence rates={metrics.map(({ key }) => ({ key, rate: rateFor(key) }))} label={`Module ${module.num} evidence`} />

              <div className="specific-objectives-heading"><h4>Specific objectives</h4><span>CAR by objective · other measures by module</span></div>
              <div className="objective-ledger-heading" aria-hidden="true">
                <span>Learning objective</span><div><span>Measure</span><span>Result</span><span>Target</span></div>
              </div>
              <ol className="specific-objectives" aria-label={`Module ${module.num} specific objectives`}>
                {module.sos.map((objective) => {
                  const readings = objective.metrics.map((metric) => ({
                    ...metric,
                    rate: metric.kpi === 'car' ? data.objectives?.[objective.id] ?? EMPTY_RATE : rateFor(metric.kpi),
                  }))
                  const statuses = readings.map((item) => metricTargetStatus(item.rate, item.target, item.up))
                  const hasMissing = statuses.includes('none')
                  const status: ObjectiveStatus = hasMissing
                    ? statuses.every((item) => item === 'none') ? 'none' : 'partial'
                    : statuses.every((item) => item === 'met') ? 'met' : 'miss'
                  return <li key={objective.id} className="specific-objective" data-state={status} aria-label={`${objective.id} ${objective.title}`}>
                    <div className="specific-objective-identity">
                      <span className="specific-objective-code">{objective.id}</span>
                      <div className="specific-objective-title">
                        <h5>{objective.title}</h5>
                        {readings.length > 1 ? <StatusBadge status={status} /> : null}
                        <details className="specific-objective-evidence">
                          <summary>{readings.length > 1 ? 'Both targets required · evidence' : 'Evidence'}</summary>
                          <p>{readings[0].kpi === 'car' ? 'This objective’s first-mastery assessments.' : 'Results across this module.'}</p>
                          {readings.map((item) => <p key={item.kpi}><strong>{KPIS.find((metric) => metric.key === item.kpi)!.abbr}</strong> · {kpiEvidence(item.kpi, item.rate)}</p>)}
                        </details>
                      </div>
                    </div>
                    <div className="specific-objective-metrics">
                      {readings.map((item) => <div className="objective-reading" data-state={metricTargetStatus(item.rate, item.target, item.up)} key={item.kpi}>
                        <span className="objective-reading-name"><span className="sr-only">{metricName(item.kpi)}</span><abbr title={metricName(item.kpi)} aria-hidden="true">{KPIS.find((metric) => metric.key === item.kpi)!.abbr}</abbr>{!item.up ? <small>Lower is better</small> : null}</span>
                        <div className="objective-reading-result"><strong>{formatKpi(item.kpi, item.rate)}</strong><StatusBadge status={metricTargetStatus(item.rate, item.target, item.up)} /></div>
                        <Goal metric={item.kpi} target={item.target} />
                      </div>)}
                    </div>
                  </li>
                })}
              </ol>
            </> : null}
          </section>
        )
      })}

      <div className="record-footnotes">
        <details className="performance-calculation">
          <summary>How these KPIs are measured</summary>
          <p>Arcane Spire practice in Modules 1–4, across all time. Replay runs are excluded. The activity range above does not change these results.</p>
          <p>These mastery KPIs are separate from the run-based finish rate above. Scenario Completion Rate measures each general objective. Command Accuracy Rate uses each specific objective’s mapped scenarios; the module summary combines its assessments. Hard-Level Completion Rate, Average Retry Count, and Retry Transfer Accuracy use module results.</p>
          {KPIS.map((metric) => <div key={metric.key}>
            <h4>{metricName(metric.key)} ({metric.abbr})</h4>
            <p>{metric.explanation}</p><p>{metric.formula}</p><p>{metric.why}</p>
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
          <p>{SUPPLEMENTARY_KPI.explanation}</p><p>{SUPPLEMENTARY_KPI.formula}</p><p>For context · no target</p>
        </details>
      </div>
    </div>
  )
}
