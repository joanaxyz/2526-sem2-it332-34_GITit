import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Activity, BookOpen, CheckCircle2, ChevronDown, Minus, X, XCircle } from 'lucide-react'
import { useState } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import { KpiRangePicker } from '@/features/admin/components/KpiRangePicker'
import {
  SupplementaryRetryCard,
  SupplementaryRetryModuleRow,
} from '@/features/admin/components/SupplementaryRetryRate'
import type { KpiDateRange } from '@/features/admin/types'
import {
  EMPTY_RATE,
  GO_SCR_TARGET,
  KPIS,
  MODULES,
  getModuleRate,
  type Rate,
  type SoMetric,
  type SpecificObjective,
  type Status,
} from '@/features/admin/utils/kpiCatalogue'
import { ALL_TIME } from '@/features/admin/utils/kpiRange'
import type { PerformanceModule } from '@/features/performance/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

// ─── helpers ──────────────────────────────────────────────────────────────────
function status(r: Rate, target: number, up: boolean): Status {
  if (r.value === null || r.denominator === 0) return 'none'
  return (up ? r.value >= target : r.value <= target) ? 'met' : 'miss'
}

// A multi-metric SO misses if any metric misses, is met only when every metric
// is met, and otherwise has no verdict yet.
function combinedStatus(statuses: Status[]): Status {
  if (statuses.includes('miss')) return 'miss'
  if (statuses.length > 0 && statuses.every(st => st === 'met')) return 'met'
  return 'none'
}

// CAR is measured per SO (from the SO-to-level mapping); every other KPI is
// measured per module.
type SoData = { module: PerformanceModule | undefined; objectives: Record<string, Rate> }

function soMetricRate(metric: SoMetric, so: SpecificObjective, data: SoData): Rate {
  if (metric.kpi === 'car') return data.objectives[so.id] ?? EMPTY_RATE
  return data.module ? getModuleRate(data.module, metric.kpi) : EMPTY_RATE
}

function soStatus(so: SpecificObjective, data: SoData): Status {
  return combinedStatus(so.metrics.map(m => status(soMetricRate(m, so, data), m.target, m.up)))
}

function fmtRate(r: Rate, pct: boolean): string {
  if (r.value === null) return '—'
  return pct ? `${r.value}%` : r.value.toFixed(2)
}

function barW(r: Rate, target: number, up: boolean): number {
  if (r.value === null) return 0
  if (up) return Math.min(100, (r.value / target) * 100)
  const max = target * 3
  return Math.max(0, 100 - Math.min(100, ((r.value - target) / (max - target)) * 100))
}

function StatusIcon({ s }: { s: Status }) {
  if (s === 'met')  return <CheckCircle2 />
  if (s === 'miss') return <XCircle />
  return <Minus />
}

// ─── KPI card ─────────────────────────────────────────────────────────────────
function KpiCard({ kpi, rate }: { kpi: typeof KPIS[number]; rate: Rate | undefined }) {
  const r: Rate = rate ?? { value: null, numerator: 0, denominator: 0 }
  const s = status(r, kpi.target, kpi.up)
  const bw = barW(r, kpi.target, kpi.up)
  const hasData = r.value !== null
  const valClass = s !== 'none' ? s : hasData ? 'has-data' : ''

  return (
    <div
      className={`dk-kpi-card ${s === 'met' ? 'is-met' : s === 'miss' ? 'is-miss' : ''}`}
      title={'tooltip' in kpi ? kpi.tooltip : undefined}
    >
      <div className="dk-kpi-top">
        <span className="dk-kpi-abbr">{kpi.abbr}</span>
        <span className={`dk-kpi-dot ${s === 'met' ? 'is-met' : s === 'miss' ? 'is-miss' : ''}`} aria-hidden="true" />
      </div>

      <div className={`dk-kpi-value ${valClass}`}>
        {fmtRate(r, kpi.pct)}
      </div>

      <div className="dk-kpi-target">
        Target: {kpi.up ? '≥' : '≤'}{kpi.target}{kpi.pct ? '%' : ''}
      </div>

      <div
        className="dk-kpi-bar"
        role="progressbar"
        aria-valuenow={bw}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={`dk-kpi-bar-fill ${s === 'met' ? 'is-met' : s === 'miss' ? 'is-miss' : ''}`}
          style={{ width: `${bw}%` }}
        />
      </div>

      <p className="dk-kpi-name">{kpi.name}</p>
      <p className="dk-kpi-evidence">
        {r.denominator > 0 ? `${r.numerator} / ${r.denominator} sessions` : 'No data yet'}
      </p>
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

function KpiRefPanel() {
  return (
    <div className="dk-ref-panel" role="region" aria-label="KPI formulas and insights">
      {KPIS.map(kpi => (
        <div key={kpi.key} className="dk-ref-entry">
          <div className="dk-ref-e-head">
            <span className="dk-ref-e-abbr">{kpi.abbr}</span>
            <span className="dk-ref-e-target">{kpi.up ? '≥' : '≤'}{kpi.target}{kpi.pct ? '%' : ''}</span>
          </div>
          <p className="dk-ref-e-name">{kpi.name}</p>
          <p className="dk-ref-e-why">{kpi.why}</p>
          <div className="dk-ref-e-formula">
            <span>Formula</span>
            <code>{kpi.formula}</code>
          </div>
        </div>
      ))}
    </div>
  )
}

// ─── SO row ───────────────────────────────────────────────────────────────────
function SoMetricCell({ metric, so, data }: { metric: SoMetric; so: SpecificObjective; data: SoData }) {
  const kpiMeta = KPIS.find(k => k.key === metric.kpi)!
  const r = soMetricRate(metric, so, data)
  const s = status(r, metric.target, metric.up)

  return (
    <div className="dk-so-kpi">
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
  const [open, setOpen] = useState<number | null>(1)

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
        const total = allStatuses.filter(s => s !== 'none').length

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
              <div className="dk-mod-body">

                {/* General Objective */}
                <div className="dk-go">
                  <div className="dk-go-top">
                    <span className="dk-go-label">General Objective</span>
                    <div className="dk-go-kpi-row">
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
  const [refOpen, setRefOpen] = useState(false)
  const [range, setRange] = useState<KpiDateRange>(ALL_TIME)
  const analytics = useQuery({
    queryKey: queryKeys.adminAnalyticsRange(range.startDate, range.endDate),
    queryFn: () => adminApi.analytics(range),
    // Keep the current numbers on screen while a new range loads.
    placeholderData: keepPreviousData,
  })
  const overview  = useQuery({ queryKey: queryKeys.adminOverview,  queryFn: adminApi.overview  })

  if (analytics.isPending) return <LoadingScreen label="Loading" />
  if (analytics.isError || !analytics.data)
    return <ErrorState title="Could not load analytics" description="Try again shortly." />

  const data     = analytics.data
  const diag     = data.runebound_performance

  // Overall SCR uses the same source and filters as the per-module SCR
  // (Runebound tier runs, Modules 1–4, replays excluded), not data.runs,
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
    <div className="dk-page">

      {/* ── page header ── */}
      <div className="dk-header">
        <div className="dk-header-left">
          <p className="dk-eyebrow">
            <Activity aria-hidden="true" />
            Runebound Turret · Modules 1–4 · replays and staff excluded
          </p>
          <h1 className="dk-title">KPI Overview</h1>
          <p className="dk-subtitle">
            Live capstone objectives — all learner sessions aggregated.
          </p>
        </div>

        <div className="dk-stats">
          <div className="dk-stat">
            <span className="dk-stat-value">
              {metCount}<span>/{KPIS.length}</span>
            </span>
            <span className="dk-stat-label">targets met</span>
          </div>
          <div className="dk-stat">
            {/* Started sessions under the header's scope: SCR's denominator. */}
            <span className="dk-stat-value">{diag.kpis.scr.denominator.toLocaleString()}</span>
            <span className="dk-stat-label">sessions</span>
          </div>
          <div className="dk-stat">
            <span className="dk-stat-value">{data.active_learners_30d}</span>
            <span className="dk-stat-label">active 30d</span>
          </div>
          {overview.data && (
            <div className="dk-stat">
              <span className="dk-stat-value">{overview.data.users.total}</span>
              <span className="dk-stat-label">registered</span>
            </div>
          )}
        </div>
      </div>

      <KpiRangePicker value={range} applied={data.kpi_range} onChange={setRange} />

      {/* ── KPI cards ── */}
      <div className="dk-section">
        <div className="dk-section-head">
          <div>
            <h2 className="dk-section-title">Overall — All Learners</h2>
            <p className="dk-section-sub">Aggregate across Modules 1–4</p>
          </div>
          <KpiRefButton open={refOpen} onToggle={() => setRefOpen(v => !v)} />
        </div>
        {refOpen && <KpiRefPanel />}
        <div className="dk-kpi-grid">
          {KPIS.map(kpi => (
            <KpiCard key={kpi.key} kpi={kpi} rate={byKey[kpi.key]} />
          ))}
        </div>
        <SupplementaryRetryCard rate={diag.kpis.retry_success_rate} />
      </div>

      {/* ── module breakdown ── */}
      <div className="dk-section">
        <div className="dk-section-head">
          <div>
            <h2 className="dk-section-title">Breakdown by Module</h2>
            <p className="dk-section-sub">General Objective + Specific Objectives SO 1.1 – SO 4.5</p>
          </div>
        </div>
        <ModuleAccordion modules={diag.modules} objectives={data.objectives} />
      </div>

    </div>
  )
}
