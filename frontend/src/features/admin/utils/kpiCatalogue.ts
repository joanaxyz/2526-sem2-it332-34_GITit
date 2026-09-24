import type { PerformanceModule } from '@/features/performance/types'

/* KPI and objective catalogues for the admin KPI Overview: the evaluation
 * KPIs (targets, formulas) and the official Specific Objectives per module. */

// ─── types ───────────────────────────────────────────────────────────────────
export type Rate = { value: number | null; numerator: number; denominator: number }
export type Status = 'met' | 'miss' | 'none'

// ─── KPI catalogue ────────────────────────────────────────────────────────────
export const KPIS = [
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

export type KpiKey = (typeof KPIS)[number]['key']

export const EMPTY_RATE: Rate = { value: null, numerator: 0, denominator: 0 }

export function getModuleRate(mod: PerformanceModule, key: KpiKey): Rate {
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
export type SoMetric = { kpi: KpiKey; target: number; up: boolean }
export type SpecificObjective = { id: string; title: string; metrics: readonly SoMetric[] }
export type ModuleObjectives = { num: number; title: string; go: string; sos: readonly SpecificObjective[] }

export const GO_SCR_TARGET = 80

const car  = (): SoMetric => ({ kpi: 'car',  target: 70, up: true })
const hlcr = (target: number): SoMetric => ({ kpi: 'hlcr', target, up: true })
const arc  = (target: number): SoMetric => ({ kpi: 'arc',  target, up: false })
const rta  = (target: number): SoMetric => ({ kpi: 'rta',  target, up: true })

export const MODULES: readonly ModuleObjectives[] = [
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
