import { LearningAnalytics } from '@/features/admin/components/LearningAnalytics'
import { soMetricRate, soStatus, type SoData } from '@/features/admin/utils/objectiveEvaluation'
import '@/styles/features/admin/learning-analytics.css'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, CheckCircle2, ChevronDown, Info, Minus, X, XCircle } from 'lucide-react'
import { useState } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import { SupplementaryRetryModuleRow } from '@/features/admin/components/SupplementaryRetryRate'
import {
  GO_SCR_TARGET,
  KPIS,
  MODULES,
  SUPPLEMENTARY_KPI,
  type CardKpi,
  type Rate,
  type SoMetric,
  type SpecificObjective,
  type Status,
} from '@/features/admin/utils/kpiCatalogue'
import { formatMetricValue, kpiEvidence, metricTargetStatus } from '@/features/performance/utils/performanceKpis'
import { ALL_TIME } from '@/features/admin/utils/kpiRange'
import type { PerformanceModule } from '@/features/performance/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { Modal } from '@/shared/components/Modal'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

// ─── helpers ──────────────────────────────────────────────────────────────────
function status(r: Rate, target: number, up: boolean): Status {
  return metricTargetStatus(r, target, up)
}

function fmtRate(r: Rate, pct: boolean): string {
  return formatMetricValue(r.value, pct)
}

function StatusIcon({ s }: { s: Status }) {
  if (s === 'met')  return <CheckCircle2 />
  if (s === 'miss') return <XCircle />
  return <Minus />
}

// ─── KPI card ─────────────────────────────────────────────────────────────────
function KpiCard({ kpi, rate, onDetails }: { kpi: CardKpi; rate: Rate | undefined; onDetails: () => void }) {
  const r: Rate = rate ?? { value: null, numerator: 0, denominator: 0 }
  // The supplementary indicator has no target: no status, bar or target line.
  const target = 'target' in kpi ? { value: kpi.target, up: kpi.up } : null
  const s: Status = target ? status(r, target.value, target.up) : 'none'
  const hasData = r.value !== null
  const valClass = s !== 'none' ? s : hasData ? 'has-data' : ''
  const stateClass = s === 'met' ? 'is-met' : s === 'miss' ? 'is-miss' : ''

  return (
    <div
      className={`dk-kpi-card ${stateClass}`}
      title={'tooltip' in kpi ? kpi.tooltip : undefined}
    >
      <div className="dk-kpi-top">
        <p className="dk-kpi-name">{'longName' in kpi ? kpi.longName : kpi.name}</p>
        <button className="dk-kpi-info" type="button" aria-label={`${kpi.abbr} metric details`} onClick={onDetails}><Info aria-hidden="true" /></button>
      </div>
      <span className="dk-kpi-abbr">{kpi.abbr}</span>
      <div className={`dk-kpi-value ${valClass}`}>{fmtRate(r, kpi.pct)}</div>
      {target ? <div className="dk-kpi-footer">
        <span className="dk-kpi-target">Target: {target.up ? '≥' : '≤'}{target.value}{kpi.pct ? '%' : ''}</span>
        <span className={`la-status is-${s}`}>{s === 'met' ? 'Met' : s === 'miss' ? 'Not met' : 'No evidence'}</span>
      </div> : <span className="dk-kpi-tag">Supplementary · No target</span>}
      <span className="la-sr-only">{kpi.name}. {kpiEvidence(kpi.key, r)}</span>
    </div>
  )
}

// ─── KPI reference panel (button only — panel rendered outside flex row) ─────
function KpiRefButton({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  return (
    <button
      className={`dk-ref-btn ${open ? 'is-open' : ''}`}
      onClick={onToggle}
      aria-expanded={open}
    >
      <BookOpen aria-hidden="true" />
      KPI Reference
      {open ? <X aria-hidden="true" /> : <ChevronDown aria-hidden="true" />}
    </button>
  )
}

const KPI_MEANING: Record<CardKpi['key'], { purpose: string; met: string; miss: string }> = {
  scr: {
    purpose: 'Shows whether learners can finish the required Git practice. A tier is completed when all its required scenarios are cleared, even if several attempts were needed.',
    met: 'Learners are completing enough of the assessed practice to meet the research target. This supports successful task completion across the required Git exercises.',
    miss: 'Completion is below the research target. Review the module results to identify where learners may need more practice or support.',
  },
  car: {
    purpose: 'Shows how efficiently learners use Git commands to solve new problems, compared with a validated solution. Efficient command use helps indicate that learners can choose appropriate steps.',
    met: 'Learners meet the target for command efficiency on scored scenarios. Their solutions use commands efficiently enough relative to the validated references.',
    miss: 'Command efficiency is below the research target. Learners may reach the solution while using extra commands, suggesting a need to practise planning the Git steps.',
  },
  hlcr: {
    purpose: 'Shows whether learners can complete the harder Git tasks. This helps assess how well they handle more demanding work beyond the easier exercises.',
    met: 'Learners meet the target for completing assessed Hard tiers. This supports their ability to handle the more challenging Git tasks in the system.',
    miss: 'Hard-tier completion is below the research target. Learners may need further practice with complex Git tasks.',
  },
  arc: {
    purpose: 'Shows how many unsuccessful attempts learners need before completing a tier. Fewer retries can suggest more deliberate problem solving and less trial and error.',
    met: 'The average retry count is within the allowed maximum. Learners who completed tiers generally needed few unsuccessful attempts to reach completion.',
    miss: 'The average retry count exceeds the allowed maximum. Learners who completed tiers needed more unsuccessful attempts than intended, suggesting room to strengthen their problem-solving approach.',
  },
  rta: {
    purpose: 'Shows whether learners can apply what they practised to an unfamiliar Git problem. Success on a new repository or goal helps assess whether their skills transfer beyond familiar exercises.',
    met: 'Learners meet the target for clearing eligible unfamiliar checkpoints on the first attempt. This supports their ability to apply practised Git skills to new problems.',
    miss: 'First-attempt success on unfamiliar checkpoints is below the target. Learners may benefit from practising a wider variety of Git problems.',
  },
  retry_success_rate: {
    purpose: 'Shows how often a retry after a failed run succeeds. This helps describe how learners recover from mistakes during Git practice.',
    met: 'Higher values mean a larger share of concluded recovery retries succeeded. This supplementary measure adds context to the five research KPIs and has no attainment target.',
    miss: '',
  },
}

function KpiRefPanel({ selected, rates, onSelect, onClose }: {
  selected: CardKpi; rates: Record<string, Rate>; onSelect: (kpi: CardKpi) => void; onClose: () => void
}) {
  const rate = rates[selected.key]
  const meaning = KPI_MEANING[selected.key]
  const verdict = 'target' in selected ? status(rate, selected.target, selected.up) : null
  const interpretation = rate.value === null || rate.denominator === 0
    ? 'There is not enough eligible evidence to interpret this result yet.'
    : verdict === 'miss' ? meaning.miss : meaning.met
  return <Modal open title="KPI Reference" onClose={onClose} dismissOnBackdropClick overlayClassName="dk-reference-overlay" className="dk-reference-drawer">
    <label className="dk-reference-selector">Metric
      <select value={selected.key} onChange={event => onSelect([...KPIS, SUPPLEMENTARY_KPI].find(kpi => kpi.key === event.target.value)!)}>
        {[...KPIS, SUPPLEMENTARY_KPI].map(kpi => <option key={kpi.key} value={kpi.key}>{kpi.abbr} — {kpi.name}</option>)}
      </select>
    </label>
    <h3>{selected.name}</h3>
    <div className="dk-reference-value">{fmtRate(rates[selected.key], selected.pct)}<span>{'target' in selected ? `Target ${selected.up ? '≥' : '≤'}${selected.target}${selected.pct ? '%' : ''}` : 'Supplementary · No target'}</span></div>
    <p>{kpiEvidence(selected.key, rates[selected.key])}</p>
    <section className="dk-reference-meaning"><h4>Why we measure it</h4><p>{meaning.purpose}</p>
      <h4>What this result suggests</h4><p>{interpretation}</p>
    </section>
    <div className="dk-reference-formula"><h4>Formula</h4><code>{selected.formula}</code></div>
    {'tooltip' in selected && <p>{selected.tooltip}</p>}
    <section className="dk-reference-method"><h4>Reporting methodology</h4>
      <p>{'why' in selected ? selected.why : selected.explanation}</p>
      <p>Live practice results give each contributing learner equal weight. Staff are excluded. CAR includes eligible fresh-content replays. Overall KPIs use learner scores, rather than averages of module results. Formal studies use frozen assignments.</p>
      <p>Interpretations describe the contributing learners as a group. A target being met can coexist with individual learners needing support. Read the five KPIs together to assess different aspects of Git performance. Establishing learning gains requires the study evaluation evidence.</p>
    </section>
  </Modal>
}
function SoMetricCell({ metric, so, data }: { metric: SoMetric; so: SpecificObjective; data: SoData }) {
  const kpiMeta = KPIS.find(k => k.key === metric.kpi)!
  const r = soMetricRate(metric, so, data)
  const s = status(r, metric.target, metric.up)

  return (
    <div className="dk-so-kpi" title={kpiEvidence(metric.kpi, r)}>
      <span className={`dk-so-kpi-chip ${s !== 'none' ? `is-${s}` : ''}`}>
        {kpiMeta.abbr}
      </span>
      <span className={`dk-so-kpi-val ${s !== 'none' ? `is-${s}` : ''}`}>
        {fmtRate(r, kpiMeta.pct)}
      </span>
      <span className="dk-target-text">
        {metric.up ? '≥' : '≤'}{metric.target}{kpiMeta.pct ? '%' : ''}
      </span>
    </div>
  )
}

function SoRow({ so, data }: { so: SpecificObjective; data: SoData }) {
  const s = soStatus(so, data)

  return (
    <div className={`dk-so-row is-${s}`} data-so={so.id}>
      <div className="dk-so-icon">
        <StatusIcon s={s} />
      </div>
      <div className="dk-so-body">
        <span className="dk-so-id">{so.id}</span>
        <p className="dk-so-text">{so.title}</p>
      </div>
      <div className="dk-so-kpis">
        {so.metrics.map(metric => (
          <SoMetricCell key={metric.kpi} metric={metric} so={so} data={data} />
        ))}
      </div>
    </div>
  )
}

// ─── module accordion ─────────────────────────────────────────────────────────
function ModuleAccordion({ modules, objectives }: { modules: PerformanceModule[]; objectives: Record<string, Rate> }) {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div className="dk-modules">
      {MODULES.map(mod => {
        const mdata  = modules.find(m => m.number === mod.num)
        const soData: SoData = { module: mdata, objectives }
        const isOpen = open === mod.num

        // GO uses SCR
        const goRate: Rate = mdata?.scr
          ? mdata.scr
          : { value: null, numerator: 0, denominator: 0 }
        const goS = status(goRate, GO_SCR_TARGET, true)

        // tally all objectives
        const allStatuses: Status[] = [goS, ...mod.sos.map(so => soStatus(so, soData))]
        const met   = allStatuses.filter(s => s === 'met').length
        const total = allStatuses.length

        const badgeClass = total === 0 ? 'none' : met === total ? 'all' : met > 0 ? 'partial' : 'none'

        return (
          <div key={mod.num} className={`dk-mod-item ${isOpen ? 'is-open' : ''}`}>
            <button
              className="dk-mod-trigger"
              onClick={() => setOpen(isOpen ? null : mod.num)}
              aria-expanded={isOpen}
            >
              <span className="dk-mod-num">M{mod.num}</span>
              <div className="dk-mod-meta">
                <span className="dk-mod-title">{mod.title}</span>
                <span className="dk-mod-hint">GO + {mod.sos.length} specific objectives</span>
              </div>
              <div className="dk-mod-right">
                {total > 0 && (
                  <span className={`dk-mod-badge ${badgeClass}`}>
                    {met}/{total} met
                  </span>
                )}
                <ChevronDown className="dk-mod-chevron" aria-hidden="true" />
              </div>
            </button>

            {isOpen && (
              <div className="dk-mod-body" tabIndex={0} role="region" aria-label={`Module ${mod.num} detailed results`}>

                {/* General Objective */}
                <div className="dk-go">
                  <div className="dk-go-top">
                    <span className="dk-go-label">General Objective</span>
                    <div className="dk-go-kpi-row" title={kpiEvidence('scr', goRate)}>
                      <span className="dk-chip">SCR</span>
                      <span className={`dk-val is-${goS}`}>
                        {goRate.value === null ? '—' : `${goRate.value}%`}
                      </span>
                      <span className="dk-target-text">≥{GO_SCR_TARGET}%</span>
                      <span className={`dk-status-icon is-${goS}`}>
                        <StatusIcon s={goS} />
                      </span>
                    </div>
                  </div>
                  <p className="dk-go-text">{mod.go}</p>
                </div>

                {/* Specific Objectives */}
                <div className="dk-so-list">
                  {mod.sos.map(so => (
                    <SoRow key={so.id} so={so} data={soData} />
                  ))}
                </div>

                {mdata && <SupplementaryRetryModuleRow rate={mdata.retry_success_rate} />}

              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── page ─────────────────────────────────────────────────────────────────────
export function AdminDashboardPage() {
  const [selectedKpi, setSelectedKpi] = useState<CardKpi | null>(null)
  const analytics = useQuery({
    queryKey: queryKeys.adminAnalyticsRange(null, null),
    queryFn: () => adminApi.analytics(ALL_TIME),
  })
  const overview  = useQuery({ queryKey: queryKeys.adminOverview,  queryFn: adminApi.overview  })

  if (analytics.isPending) return <LoadingScreen label="Loading" />
  if (analytics.isError || !analytics.data)
    return <ErrorState title="Could not load analytics" description="Try again shortly." />

  const data     = analytics.data
  const diag     = data.runebound_performance

  // Overall SCR uses the same source and filters as the per-module SCR
  // (Arcane Spire tier runs, Modules 1–4, replays excluded), not data.runs,
  // which spans every story and run type.
  const byKey: Record<string, Rate> = {
    scr:  diag.kpis.scr,
    car:  diag.kpis.car,
    hlcr: diag.kpis.hlcr,
    arc:  diag.kpis.arc,
    rta:  diag.kpis.rta,
  }

  const metCount = KPIS.filter(k => {
    const r = byKey[k.key]
    return r && status(r, k.target, k.up) === 'met'
  }).length

  return (
    <div className="dk-page dk-analytics">

      {/* ── page header ── */}
      <div className="dk-header dk-overview-header">
        <div className="dk-header-left">
          <p className="dk-eyebrow">
            Arcane Spire · Modules 1–4
          </p>
          <h1 className="dk-title">KPI Overview</h1>
        </div>

        <div className="dk-stats">
          <div className="dk-stat dk-stat-primary">
            <span className="dk-stat-value">
              {metCount}<span>/{KPIS.length}</span>
            </span>
            <span className="dk-stat-label">targets met</span>
          </div>
          <div className="dk-stat">
            {/* Activity coverage stays separate from participant-mean KPI denominators. */}
            <span className="dk-stat-value">{diag.samples.attempted_tiers.toLocaleString()}</span>
            <span className="dk-stat-label">attempted tiers</span>
          </div>
          <div className="dk-stat">
            <span className="dk-stat-value">{data.active_learners_30d}</span>
            <span className="dk-stat-label" title="Active learners across all activity in the last 30 days">active · 30 days</span>
          </div>
          {overview.data && (
            <div className="dk-stat">
              <span className="dk-stat-value">{overview.data.users.total}</span>
              <span className="dk-stat-label" title="All registered users, across all time">registered</span>
            </div>
          )}
        </div>
      </div>

      {analytics.isFetching && <p className="la-update" role="status">Updating analytics…</p>}

      {/* ── KPI cards ── */}
      <div className="dk-section">
        <div className="dk-section-head">
          <div>
            <h2 className="dk-section-title">Overall KPI Results</h2>
            <p className="dk-section-sub">Five research metrics across Modules 1–4 · All time</p>
          </div>
          <KpiRefButton open={selectedKpi !== null} onToggle={() => setSelectedKpi(KPIS[0])} />
        </div>
        {selectedKpi && <KpiRefPanel selected={selectedKpi} rates={{ ...byKey, retry_success_rate: diag.kpis.retry_success_rate }} onSelect={setSelectedKpi} onClose={() => setSelectedKpi(null)} />}
        <div className="dk-kpi-grid">
          {KPIS.map(kpi => (
            <KpiCard key={kpi.key} kpi={kpi} rate={byKey[kpi.key]} onDetails={() => setSelectedKpi(kpi)} />
          ))}
          <KpiCard kpi={SUPPLEMENTARY_KPI} rate={diag.kpis.retry_success_rate} onDetails={() => setSelectedKpi(SUPPLEMENTARY_KPI)} />
        </div>
      </div>

      <LearningAnalytics summary={diag} objectives={data.objectives} />

      {/* ── module breakdown ── */}
      <div className="dk-section">
        <div className="dk-section-head">
          <div>
            <h2 className="dk-section-title">Detailed Module Results</h2>
            <p className="dk-section-sub">Open a module to review its research objectives and results.</p>
          </div>
        </div>
        <ModuleAccordion modules={diag.modules} objectives={data.objectives} />
      </div>

    </div>
  )
}
