import { useId, useState, type CSSProperties } from 'react'
import { ArrowDownRight, ArrowUpRight, Check, ChevronRight, GitBranch, RotateCcw, Swords, Target, Terminal } from 'lucide-react'

import {
  KPIS, SUPPLEMENTARY_KPI, formatKpi, kpiEvidence, metricStatus,
  type CardKpi, type EvidenceKey,
} from '@/features/performance/utils/performanceKpis'
import type { PerformanceSummary, RateMetric } from '@/features/performance/types'

const ICONS = {
  scr: Target, car: Terminal, hlcr: Swords, arc: RotateCcw,
  rta: GitBranch, retry_success_rate: RotateCcw,
}

function measured(rate: RateMetric) {
  return rate.value !== null && rate.denominator > 0
}

/** Geometry only: the scalar track expands when a retry average exceeds its goal. */
function trackStyle(definition: CardKpi, rate: RateMetric): CSSProperties {
  const ceiling = definition.key === 'arc' ? Math.max(4, rate.value ?? 0) : 100
  return {
    '--signal-value': Math.max(0, Math.min(1, (rate.value ?? 0) / ceiling)),
    '--signal-goal': `${'target' in definition ? (definition.target / ceiling) * 100 : 0}%`,
  } as CSSProperties
}

function Signal({
  definition, rate, selected, onSelect, detailId,
}: {
  definition: CardKpi
  rate: RateMetric
  selected: boolean
  onSelect: () => void
  detailId: string
}) {
  const Icon = ICONS[definition.key]
  const status = metricStatus(definition.key, rate)
  const hasData = measured(rate)
  const state = !hasData ? 'Not measured yet'
    : definition.key === 'retry_success_rate' ? 'For context'
      : status === 'met' ? 'On track' : 'Keep practicing'

  return (
    <button
      type="button"
      className={`performance-signal${selected ? ' is-selected' : ''}`}
      data-state={hasData ? status : 'empty'}
      aria-pressed={selected}
      aria-controls={detailId}
      onClick={onSelect}
      style={trackStyle(definition, rate)}
    >
      <span className="performance-signal-icon" aria-hidden="true"><Icon /></span>
      <span className="performance-signal-copy">
        <span className="performance-signal-name">{definition.label}</span>
        <span className="performance-signal-evidence">{kpiEvidence(definition.key, rate)}</span>
        <span className="performance-signal-track" aria-hidden="true">
          <i />
          {'target' in definition ? <b /> : null}
        </span>
      </span>
      <span className="performance-signal-reading">
        <strong>{formatKpi(definition.key, rate)}</strong>
        <span className="performance-signal-state">
          {status === 'met' ? <Check aria-hidden="true" /> : null}{state}
        </span>
        <small>
          {'target' in definition
            ? `Goal ${definition.up ? '≥' : '≤'}${definition.target}${definition.pct ? '%' : ''}`
            : 'No target'}
        </small>
      </span>
      <ChevronRight className="performance-signal-chevron" aria-hidden="true" />
    </button>
  )
}

function ModuleComparison({ data, selected }: { data: PerformanceSummary; selected: EvidenceKey }) {
  if (selected === 'car') {
    return (
      <div className="performance-overall-note">
        <Terminal aria-hidden="true" />
        <h4>One view across your commands</h4>
        <p>Command acceptance is measured across Modules 1–4 together. A per-module breakdown is not available.</p>
        <p>{kpiEvidence(selected, data.kpis.car)}</p>
      </div>
    )
  }
  const modules = data.modules.filter((module) =>
    selected === 'rta' ? [3, 4].includes(module.number) : [1, 2, 3, 4].includes(module.number),
  )
  const ceiling = selected === 'arc'
    ? Math.max(1, ...modules.map((module) => module.arc.value ?? 0))
    : 100

  return (
    <section className="performance-modules" aria-label="Module comparison">
      <div className="performance-module-heading">
        <h4>Across your modules</h4>
        <span>{selected === 'arc' ? 'Relative scale · fewer is better' : '0–100%'}</span>
      </div>
      {modules.length === 0 ? <p>No module results available yet.</p> : (
        <ol>
          {modules.map((module) => {
            const rate = module[selected]
            const hasData = measured(rate)
            const percent = Math.max(0, Math.min(100, ((rate.value ?? 0) / ceiling) * 100))
            return (
              <li key={module.number} data-empty={hasData ? undefined : 'true'}>
                <span className="performance-module-index">M{module.number}</span>
                <div className="performance-module-data">
                  <div><span>{module.title}</span><strong>{formatKpi(selected, rate)}</strong></div>
                  <div className="performance-module-track" aria-hidden="true">
                    <i style={{ transform: `scaleX(${percent / 100})` }} />
                  </div>
                  <small>{kpiEvidence(selected, rate)}</small>
                </div>
              </li>
            )
          })}
        </ol>
      )}
      <p className="performance-module-footnote">Module results describe your practice. Goals above apply to your overall record.</p>
    </section>
  )
}

/** One server response; selection changes only the reading, never the data. */
export function LearnerPerformanceInstrument({ data }: { data: PerformanceSummary }) {
  const [selected, setSelected] = useState<EvidenceKey>('scr')
  const detailId = useId()
  const definition = [...KPIS, SUPPLEMENTARY_KPI].find((kpi) => kpi.key === selected)!
  const rate = data.kpis[selected]
  const Icon = ICONS[selected]
  const Direction = selected === 'arc' ? ArrowDownRight : ArrowUpRight

  return (
    <div className="performance-instrument">
      <div className="performance-signal-rail" role="group" aria-label="Practice measures">
        {KPIS.map((kpi) => (
          <Signal
            definition={kpi} rate={data.kpis[kpi.key]} selected={selected === kpi.key}
            onSelect={() => setSelected(kpi.key)} detailId={detailId} key={kpi.key}
          />
        ))}
        <div className="performance-context-label">For context <span>your recovery record</span></div>
        <Signal
          definition={SUPPLEMENTARY_KPI} rate={data.kpis.retry_success_rate}
          selected={selected === 'retry_success_rate'} onSelect={() => setSelected('retry_success_rate')}
          detailId={detailId}
        />
      </div>
      <section className="performance-detail" id={detailId} aria-label={`${definition.label} details`} data-state={measured(rate) ? metricStatus(selected, rate) : 'empty'}>
        <header>
          <span className="performance-detail-icon" style={trackStyle(definition, rate)} aria-hidden="true">
            <svg className="performance-orbit" viewBox="0 0 80 80">
              <circle className="performance-orbit-ticks" cx="40" cy="40" r="37" pathLength="100" />
              <circle className="performance-orbit-track" cx="40" cy="40" r="30" />
              <circle className="performance-orbit-reading" cx="40" cy="40" r="30" pathLength="100" />
            </svg>
            <Icon />
          </span>
          <div>
            <h3>{definition.label}</h3>
            <p>{definition.scope}</p>
          </div>
        </header>
        <p className="performance-explanation">{definition.explanation}</p>
        {!measured(rate) ? <p className="performance-empty-hint">{definition.emptyHint}</p> : null}
        {selected !== 'retry_success_rate' ? (
          <p className="performance-direction"><Direction aria-hidden="true" />
            {selected === 'arc' ? 'Fewer retries per finish is better' : 'A higher rate is better'}
          </p>
        ) : <p className="performance-direction">Supplementary measure · no goal to meet</p>}
        <ModuleComparison data={data} selected={selected} />
        <details className="performance-calculation" key={selected}>
          <summary>How this is measured</summary>
          <p><strong>{definition.abbr}</strong> · {definition.name}</p>
          <p>{definition.formula}</p>
          <p>{selected === 'rta'
            ? 'Only the first retry directly after a failure counts, and only when its starting repository or goal changes. Failed and abandoned eligible retries count; runs still in progress do not.'
            : selected === 'retry_success_rate'
              ? 'Includes any run with a prior run, including repeats after a success. Abandoned runs are excluded. This is separate from changed-retry transfer.'
              : 'Practice runs in Modules 1–4, across all time. Replay runs are excluded. The activity range above does not change this record.'}</p>
        </details>
      </section>
    </div>
  )
}
