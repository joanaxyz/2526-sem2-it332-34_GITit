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
const MODULES = [
  {
    num: 1,
    title: 'Local Repository Foundations',
    go: 'Learners can confidently manage a local Git repository by initializing, staging, committing, and manipulating repository states without reference to external materials.',
    sos: [
      { id: 'SO 1.1', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can initialize a Git repository (git init) and verify its creation.' },
      { id: 'SO 1.2', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can clone a remote repository (git clone) and navigate the resulting directory structure.' },
      { id: 'SO 1.3', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can stage files (git add) and commit changes (git commit) with descriptive messages.' },
      { id: 'SO 1.4', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can perform partial staging (git add -p) to select specific hunks of changes.' },
      { id: 'SO 1.5', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can amend the most recent commit (git commit --amend) to correct messages or staged content.' },
      { id: 'SO 1.6', kpi: 'car' as KpiKey, target: 70, up: true,  text: 'Learners can unstage files (git restore --staged) and discard working-directory changes (git restore).' },
      { id: 'SO 1.7', kpi: 'hlcr' as KpiKey, target: 70, up: true, text: 'Learners demonstrate independent management of local repository operations without hints or scaffolding in hard-tier scenarios.' },
      { id: 'SO 1.8', kpi: 'arc' as KpiKey, target: 2,  up: false, text: 'Learners show efficient repository-state reasoning with ≤2 retries on average across Module 1 scenarios.' },
    ],
  },
  {
    num: 2,
    title: 'Branching and Collaboration',
    go: 'Learners can create and manage branches, integrate remote collaboration workflows, and handle stash and merge operations to support team-based development.',
    sos: [
      { id: 'SO 2.1',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can create a new branch (git switch -c / git branch) and switch between branches.' },
      { id: 'SO 2.2',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can stash work in progress (git stash) and restore it (git stash pop).' },
      { id: 'SO 2.3',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can merge branches using fast-forward, merge commit, and squash strategies.' },
      { id: 'SO 2.4',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can push a local branch to a remote repository (git push) and set an upstream.' },
      { id: 'SO 2.5',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can pull remote changes (git pull / git fetch + git merge) into a local branch.' },
      { id: 'SO 2.6',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can delete local and remote branches safely after merging.' },
      { id: 'SO 2.7',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can inspect branch history with git log and identify divergence points.' },
      { id: 'SO 2.8',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can rebase a feature branch onto another branch (git rebase) in a clean linear scenario.' },
      { id: 'SO 2.9',  kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can cherry-pick a specific commit onto the current branch (git cherry-pick).' },
      { id: 'SO 2.10', kpi: 'hlcr' as KpiKey, target: 70, up: true,  text: 'Learners demonstrate independent branch management in hard-tier scenarios without scaffolding.' },
      { id: 'SO 2.11', kpi: 'arc' as KpiKey,  target: 2,  up: false, text: 'Learners show reduced trial-and-error in collaboration workflows with ≤2 average retries across Module 2.' },
    ],
  },
  {
    num: 3,
    title: 'Conflict Resolution',
    go: 'Learners can identify, interpret, and resolve merge conflicts correctly, and transfer that reasoning to novel conflict scenarios independently.',
    sos: [
      { id: 'SO 3.1', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can identify a merge conflict from git output and locate conflict markers in affected files.' },
      { id: 'SO 3.2', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can manually resolve a conflict by editing the file, removing all markers, and staging the result.' },
      { id: 'SO 3.3', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can abort an in-progress merge or rebase (git merge --abort / git rebase --abort) when needed.' },
      { id: 'SO 3.4', kpi: 'hlcr' as KpiKey, target: 70, up: true,  text: 'Learners independently resolve conflicts in hard-tier scenarios without step-by-step guidance.' },
      { id: 'SO 3.5', kpi: 'rta' as KpiKey,  target: 65, up: true,  text: 'Learners demonstrate transferable conflict-resolution reasoning with ≤2 retries on average and ≥65% retry-to-success rate.' },
    ],
  },
  {
    num: 4,
    title: 'Advanced Recovery and History',
    go: 'Learners can navigate and recover lost work using reflog, revert, and reset, and demonstrate deliberate history-manipulation strategies under novel conditions.',
    sos: [
      { id: 'SO 4.1', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can use git reflog to locate a lost commit hash and restore it to a branch.' },
      { id: 'SO 4.2', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can revert a pushed commit safely using git revert without rewriting shared history.' },
      { id: 'SO 4.3', kpi: 'car' as KpiKey,  target: 70, up: true,  text: 'Learners can use git reset (--soft, --mixed, --hard) appropriately depending on the recovery goal.' },
      { id: 'SO 4.4', kpi: 'hlcr' as KpiKey, target: 65, up: true,  text: 'Learners independently perform recovery operations in hard-tier scenarios with ≥65% hard-level completion.' },
      { id: 'SO 4.5', kpi: 'rta' as KpiKey,  target: 65, up: true,  text: 'Learners show deliberate recovery reasoning with ≤3 average retries and ≥65% retry-to-success rate across Module 4.' },
    ],
  },
] as const

// ─── helpers ──────────────────────────────────────────────────────────────────
function status(r: Rate, target: number, up: boolean): Status {
  if (r.value === null || r.denominator === 0) return 'none'
  return (up ? r.value >= target : r.value <= target) ? 'met' : 'miss'
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
function SoRow({ so, modData }: {
  so: { id: string; kpi: KpiKey; target: number; up: boolean; text: string }
  modData: PerformanceModule | undefined
}) {
  const kpiMeta = KPIS.find(k => k.key === so.kpi)!
  const r: Rate = modData ? getModuleRate(modData, so.kpi) : EMPTY_RATE
  const s = status(r, so.target, so.up)
  const valStr = r.value === null ? '—' : kpiMeta.pct ? `${r.value}%` : r.value.toFixed(2)

  return (
    <div className={`dk-so-row is-${s}`}>
      <div className="dk-so-icon">
        <StatusIcon s={s} />
      </div>
      <div className="dk-so-body">
        <span className="dk-so-id">{so.id}</span>
        <p className="dk-so-text">{so.text}</p>
      </div>
      <div className="dk-so-kpi">
        <span className={`dk-so-kpi-chip ${s !== 'none' ? `is-${s}` : ''}`}>
          {kpiMeta.abbr}
        </span>
        <span className={`dk-so-kpi-val ${s !== 'none' ? `is-${s}` : ''}`}>
          {valStr}
        </span>
        <span className="dk-target-text">
          {so.up ? '≥' : '≤'}{so.target}{kpiMeta.pct ? '%' : ''}
        </span>
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
        const goS = status(goRate, 80, true)

        // tally all objectives
        const allStatuses: Status[] = [
          goS,
          ...mod.sos.map(so => {
            const r: Rate = mdata ? getModuleRate(mdata, so.kpi) : EMPTY_RATE
            return status(r, so.target, so.up)
          }),
        ]
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
                      <span className="dk-target-text">≥80%</span>
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
