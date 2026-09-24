import { useQuery } from '@tanstack/react-query'
import { Activity, BookOpen, CheckCircle2, ChevronDown, Minus, X, XCircle } from 'lucide-react'
import { useState } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import type { PerformanceModule } from '@/features/performance/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

// ─── types ───────────────────────────────────────────────────────────────────
type Rate = { value: number | null; numerator: number; denominator: number }
type Status = 'met' | 'miss' | 'none'

// ─── KPI catalogue ────────────────────────────────────────────────────────────
const KPIS = [
  {
    key: 'scr',
    abbr: 'SCR',
    name: 'Scenario Completion Rate',
    target: 80,
    up: true,
    pct: true,
    formula: 'Completed sessions ÷ Started sessions × 100',
    why: 'Measures how many learners finish a scenario without dropping out. Below 80% means scenarios are too confusing, too long, or the feedback isn\'t helping recovery.',
  },
  {
    key: 'car',
    abbr: 'CAR',
    name: 'Command Accuracy Rate',
    target: 70,
    up: true,
    pct: true,
    formula: 'Processable commands ÷ Total submitted commands × 100',
    why: 'Tracks how well learners type commands the simulator can understand. Low CAR means learners are guessing — field guide lessons need more worked examples.',
  },
  {
    key: 'hlcr',
    abbr: 'HLCR',
    name: 'Hard-Level Completion Rate',
    target: 70,
    up: true,
    pct: true,
    formula: 'Hard-difficulty tiers completed ÷ Hard-difficulty tiers started × 100',
    why: 'Hard tiers test whether learners can apply skills independently, not just in guided scenarios. Below 70% means the jump from normal to hard is too steep.',
  },
  {
    key: 'arc',
    abbr: 'ARC',
    name: 'Avg Retry Count',
    target: 2,
    up: false,
    pct: false,
    formula: 'Total retry indices across completed sessions ÷ Completed sessions',
    why: 'How many times on average a learner retries before succeeding. ≤2 is healthy. Above 3, learners are stuck in a loop — the failure feedback isn\'t actionable.',
  },
  {
    key: 'rta',
    abbr: 'RTA',
    name: 'Retry Transfer Accuracy',
    target: 65,
    up: true,
    pct: true,
    formula: 'Successful first-attempt completions on changed-variant retry sessions ÷ all changed-variant retry sessions × 100',
    why: 'Measures skill transfer: after a failure, does the learner complete the first retry when the scenario is structurally changed (a different starting repository or target)? Modules 3–4 only.',
    tooltip: 'RTA measures skill transfer to structurally changed scenarios in Modules 3–4: the first retry after a failure counts only when its starting repository or target state differs from the failed attempt.',
  },
] as const

type KpiKey = (typeof KPIS)[number]['key']

const EMPTY_RATE: Rate = { value: null, numerator: 0, denominator: 0 }

function getModuleRate(mod: PerformanceModule, key: KpiKey): Rate {
  if (key === 'scr') return mod.scr
  if (key === 'hlcr') return mod.hlcr
  if (key === 'arc') return mod.arc
  if (key === 'rta') return mod.rta
  return EMPTY_RATE
}

// ─── full capstone objectives structure ───────────────────────────────────────
// Official Specific Objectives (Proposal, SO 1.1 – SO 4.5). Each General
// Objective is measured by module SCR ≥ 80%. Per-SO targets override the
// default card targets (e.g. SO 4.4 HLCR ≥ 65%, SO 4.5 ARC ≤ 3). An SO with two
// metrics is met only when both are met.
type SoMetric = { kpi: KpiKey; target: number; up: boolean }
type SpecificObjective = { id: string; title: string; metrics: readonly SoMetric[] }
type ModuleObjectives = { num: number; title: string; go: string; sos: readonly SpecificObjective[] }

const GO_SCR_TARGET = 80

const car  = (): SoMetric => ({ kpi: 'car',  target: 70, up: true })
const hlcr = (target: number): SoMetric => ({ kpi: 'hlcr', target, up: true })
const arc  = (target: number): SoMetric => ({ kpi: 'arc',  target, up: false })
const rta  = (target: number): SoMetric => ({ kpi: 'rta',  target, up: true })

const MODULES: readonly ModuleObjectives[] = [
  {
    num: 1,
    title: 'Local Repository Foundations',
    go: 'Learners can confidently manage a local Git repository by initializing, staging, committing, and manipulating repository states without reference to external materials.',
    sos: [
      { id: 'SO 1.1', title: 'Initializing Repositories',               metrics: [car()] },
      { id: 'SO 1.2', title: 'Cloning Remote Repositories',             metrics: [car()] },
      { id: 'SO 1.3', title: 'Staging and Committing',                  metrics: [car()] },
      { id: 'SO 1.4', title: 'Partial Staging',                         metrics: [car()] },
      { id: 'SO 1.5', title: 'Amending Commits',                        metrics: [car()] },
      { id: 'SO 1.6', title: 'Unstaging and Discarding Changes',        metrics: [car()] },
      { id: 'SO 1.7', title: 'Independent Local Repository Management', metrics: [hlcr(70)] },
      { id: 'SO 1.8', title: 'Efficient Repository-State Reasoning',    metrics: [arc(2)] },
    ],
  },
  {
    num: 2,
    title: 'Branching and Collaboration',
    go: 'Learners can create and manage branches, integrate remote collaboration workflows, and handle stash and merge operations to support team-based development.',
    sos: [
      { id: 'SO 2.1',  title: 'Creating and Switching Branches',                 metrics: [car()] },
      { id: 'SO 2.2',  title: 'Branch Naming Conventions and Housekeeping',      metrics: [car()] },
      { id: 'SO 2.3',  title: 'Stashing Work in Progress',                       metrics: [car()] },
      { id: 'SO 2.4',  title: 'Pushing to a Remote',                             metrics: [car()] },
      { id: 'SO 2.5',  title: 'Fetching and Pulling from a Remote',              metrics: [car()] },
      { id: 'SO 2.6',  title: 'Reconciling Diverged Local and Remote Histories', metrics: [car()] },
      { id: 'SO 2.7',  title: 'Completing Branch Merges',                        metrics: [car()] },
      { id: 'SO 2.8',  title: 'Squash Merging',                                  metrics: [car()] },
      { id: 'SO 2.9',  title: 'Deleting and Recovering Remote Branches',         metrics: [car()] },
      { id: 'SO 2.10', title: 'Independent Branch and Collaboration Management', metrics: [hlcr(70)] },
      { id: 'SO 2.11', title: 'Reduced Trial-and-Error Branching',               metrics: [arc(2)] },
    ],
  },
  {
    num: 3,
    title: 'Conflict Resolution',
    go: 'Learners can identify, interpret, and resolve merge conflicts correctly, and transfer that reasoning to novel conflict scenarios independently.',
    sos: [
      { id: 'SO 3.1', title: 'Resolving Merge Conflicts Manually',         metrics: [car()] },
      { id: 'SO 3.2', title: 'Resolving Conflicts Using a Merge Tool',     metrics: [car()] },
      { id: 'SO 3.3', title: 'Cherry-Picking Commits',                     metrics: [car()] },
      { id: 'SO 3.4', title: 'Independent Conflict Resolution',            metrics: [hlcr(70)] },
      { id: 'SO 3.5', title: 'Transferable Conflict-Resolution Reasoning', metrics: [rta(65), arc(2)] },
    ],
  },
  {
    num: 4,
    title: 'Advanced Recovery and History',
    go: 'Learners can navigate and recover lost work using reflog, revert, and reset, and demonstrate deliberate history-manipulation strategies under novel conditions.',
    sos: [
      { id: 'SO 4.1', title: 'Recovering from Hard Resets',          metrics: [car()] },
      { id: 'SO 4.2', title: 'Reversing Pushed Commits Safely',      metrics: [car()] },
      { id: 'SO 4.3', title: 'Completing Rebase Recovery Sequences', metrics: [car()] },
      { id: 'SO 4.4', title: 'Independent Recovery Operations',      metrics: [hlcr(65)] },
      { id: 'SO 4.5', title: 'Reduced Trial-and-Error Recovery',     metrics: [rta(65), arc(3)] },
    ],
  },
]

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

function soMetricRate(metric: SoMetric, modData: PerformanceModule | undefined): Rate {
  return modData ? getModuleRate(modData, metric.kpi) : EMPTY_RATE
}

function soStatus(so: SpecificObjective, modData: PerformanceModule | undefined): Status {
  return combinedStatus(so.metrics.map(m => status(soMetricRate(m, modData), m.target, m.up)))
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
function SoMetricCell({ metric, modData }: { metric: SoMetric; modData: PerformanceModule | undefined }) {
  const kpiMeta = KPIS.find(k => k.key === metric.kpi)!
  const r = soMetricRate(metric, modData)
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

function SoRow({ so, modData }: { so: SpecificObjective; modData: PerformanceModule | undefined }) {
  const s = soStatus(so, modData)

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
          <SoMetricCell key={metric.kpi} metric={metric} modData={modData} />
        ))}
      </div>
    </div>
  )
}

// ─── module accordion ─────────────────────────────────────────────────────────
function ModuleAccordion({ modules }: { modules: PerformanceModule[] }) {
  const [open, setOpen] = useState<number | null>(1)

  return (
    <div className="dk-modules">
      {MODULES.map(mod => {
        const mdata  = modules.find(m => m.number === mod.num)
        const isOpen = open === mod.num

        // GO uses SCR
        const goRate: Rate = mdata?.scr
          ? mdata.scr
          : { value: null, numerator: 0, denominator: 0 }
        const goS = status(goRate, GO_SCR_TARGET, true)

        // tally all objectives
        const allStatuses: Status[] = [goS, ...mod.sos.map(so => soStatus(so, mdata))]
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
                    <SoRow key={so.id} so={so} modData={mdata} />
                  ))}
                </div>

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
  const analytics = useQuery({ queryKey: queryKeys.adminAnalytics, queryFn: adminApi.analytics })
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
            Runebound Turret · Modules 1–4 · replays excluded
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
            <span className="dk-stat-value">{data.runs.total.toLocaleString()}</span>
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
      </div>

      {/* ── module breakdown ── */}
      <div className="dk-section">
        <div className="dk-section-head">
          <div>
            <h2 className="dk-section-title">Breakdown by Module</h2>
            <p className="dk-section-sub">General Objective + Specific Objectives SO 1.1 – SO 4.5</p>
          </div>
        </div>
        <ModuleAccordion modules={diag.modules} />
      </div>

    </div>
  )
}
