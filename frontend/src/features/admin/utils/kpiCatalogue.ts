import { KPIS, type KpiKey } from '@/features/performance/utils/performanceKpis'

export { KPIS, SUPPLEMENTARY_KPI, EMPTY_RATE, getModuleRate } from '@/features/performance/utils/performanceKpis'
export type { Rate, Status, CardKpi } from '@/features/performance/utils/performanceKpis'

// ─── full capstone objectives structure ───────────────────────────────────────
// Official Specific Objectives (Proposal, SO 1.1 – SO 4.5). Each General
// Objective is measured by module SCR ≥ 80%. Per-SO targets override the
// default card targets (e.g. SO 4.4 HLCR ≥ 65%, SO 4.5 ARC ≤ 3). An SO with two
// metrics is met only when both are met.
export type SoMetric = { kpi: KpiKey; target: number; up: boolean }
export type SpecificObjective = { id: string; title: string; metrics: readonly SoMetric[] }
export type ModuleObjectives = { num: number; title: string; go: string; sos: readonly SpecificObjective[] }

export const GO_SCR_TARGET = KPIS.find((kpi) => kpi.key === 'scr')!.target

const car  = (): SoMetric => ({ kpi: 'car', target: KPIS.find((kpi) => kpi.key === 'car')!.target, up: true })
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
