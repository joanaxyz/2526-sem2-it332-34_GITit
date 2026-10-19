import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import type { PerformanceModule, RateMetric } from '../types'

/* Display semantics shared by learner Progress and Admin. Executable formulas
 * remain server-owned; these strings explain the response, never compute it. */

// ─── types ───────────────────────────────────────────────────────────────────
export type Rate = RateMetric
export type Status = 'met' | 'miss' | 'none'

// ─── KPI catalogue ────────────────────────────────────────────────────────────
export const KPIS = [
  {
    key: 'scr',
    label: 'Runs finished',
    explanation: 'How often you finish a practice run you start.',
    scope: 'Modules 1–4 · replay runs excluded',
    emptyHint: 'Start a practice run to begin your record.',
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
    label: 'Commands accepted',
    explanation: 'Commands Git could understand, even when they did not reach the goal yet.',
    scope: 'Modules 1–4 · overall only',
    emptyHint: 'Submit a command in practice to begin measuring this.',
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
    label: 'Hard runs cleared',
    explanation: 'How often you finish hard practice runs with less guidance.',
    scope: 'Modules 1–4 · hard difficulty',
    emptyHint: 'Try a hard run when you are ready.',
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
    label: 'Retries per finish',
    explanation: 'The average retry count attached to your completed runs. Fewer means less trial and error.',
    scope: 'Modules 1–4 · completed runs only',
    emptyHint: 'Finish a practice run to see your retry average.',
    abbr: 'ARC',
    name: 'Avg Retry Count',
    longName: 'Average Retry Count',
    target: 2,
    up: false,
    pct: false,
    formula: 'Total retry indices across completed sessions ÷ Completed sessions',
    why: 'How many times on average a learner retries before succeeding. ≤2 is healthy. Above 3, learners are stuck in a loop — the failure feedback isn\'t actionable.',
  },
  {
    key: 'rta',
    label: 'Changed retries cleared',
    explanation: 'After a failure, can you clear the first retry when its starting repository or goal changes?',
    scope: 'Modules 3–4 · first changed retry after failure',
    emptyHint: 'Measured on changed retries in Modules 3–4. No eligible retries yet.',
    abbr: 'RTA',
    name: 'Retry Transfer Accuracy',
    target: 65,
    up: true,
    pct: true,
    formula: 'Successful first-attempt completions on changed-variant retry sessions ÷ all changed-variant retry sessions × 100',
    why: 'Measures skill transfer: after a failure, does the learner complete the first retry when the scenario is structurally changed (a different starting repository or target)? Modules 3–4 only.',
    tooltip: 'RTA measures skill transfer to structurally changed scenarios in Modules 3–4: the first retry after a failure counts only when its starting repository or target state differs from the failed attempt.',
  },
] as const satisfies readonly { key: Exclude<keyof ApiSchemas['PerformanceKpiSet'], 'retry_success_rate' | 'rtr'>; [field: string]: unknown }[]

export type KpiKey = (typeof KPIS)[number]['key']

/** The old RTR measure, shown next to the evaluation KPIs for context. It has
 * no target, so it never counts toward "targets met". */
export const SUPPLEMENTARY_KPI = {
  key: 'retry_success_rate',
  label: 'Retry recovery',
  explanation: 'Completed runs that followed an earlier run, across any variant or attempt. Abandoned runs are excluded.',
  scope: 'Modules 1–4 · for context, no target',
  emptyHint: 'This appears once you try another run after an earlier one.',
  formula: 'Completed runs with a prior run ÷ non-abandoned runs with a prior run × 100',
  abbr: 'RSR',
  name: 'Retry Success Rate (supplementary)',
  pct: true,
  tooltip:
    'Share of retry sessions that eventually ended in completion, any variant, any attempt. ' +
    'Supplementary indicator only; RTA is the evaluation KPI for SO 3.5, SO 4.5 and RQ4.',
} as const

/** Any card on the Overall row: an evaluation KPI (with a target) or the
 * supplementary indicator (without one). */
export type CardKpi = (typeof KPIS)[number] | typeof SUPPLEMENTARY_KPI

export const EMPTY_RATE: Rate = { value: null, numerator: 0, denominator: 0 }

export function getModuleRate(mod: PerformanceModule, key: KpiKey): Rate {
  if (key === 'scr') return mod.scr
  if (key === 'hlcr') return mod.hlcr
  if (key === 'arc') return mod.arc
  if (key === 'rta') return mod.rta
  return EMPTY_RATE
}


export type EvidenceKey = KpiKey | typeof SUPPLEMENTARY_KPI.key

/** "1 retry" / "3 retries". */
function counted(value: number, singular: string, plural: string) {
  return `${value.toLocaleString()} ${value === 1 ? singular : plural}`
}

/** What each KPI's numerator and denominator count, in the words of its formula. */
const EVIDENCE: Record<EvidenceKey, { some: (n: number, d: number) => string; none: string }> = {
  // Completed sessions ÷ started sessions.
  scr: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'session', 'sessions')} completed`,
    none: 'No sessions yet',
  },
  // Processable commands ÷ submitted commands.
  car: {
    some: (n, d) => `${n.toLocaleString()} processable / ${counted(d, 'submitted command', 'submitted commands')}`,
    none: 'No commands yet',
  },
  // Hard sessions completed ÷ hard sessions started.
  hlcr: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'hard session', 'hard sessions')} completed`,
    none: 'No hard sessions yet',
  },
  // Total retries (retry_index) across completed sessions ÷ completed sessions.
  arc: {
    some: (n, d) =>
      `${counted(n, 'retry', 'retries')} across ${counted(d, 'completed session', 'completed sessions')}`,
    none: 'No completed sessions yet',
  },
  // Successful eligible retries ÷ eligible changed-variant retries.
  rta: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'eligible retry', 'eligible retries')} succeeded`,
    none: 'No eligible retries yet',
  },
  // Retry sessions that completed ÷ retry sessions.
  retry_success_rate: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'retry session', 'retry sessions')} completed`,
    none: 'No retry sessions yet',
  },
}

export function kpiEvidence(key: EvidenceKey, rate: Rate) {
  const units = EVIDENCE[key]
  return rate.denominator > 0 ? units.some(rate.numerator, rate.denominator) : units.none
}

/** Null and no observations are distinct from a measured zero. */
export function metricStatus(key: EvidenceKey, rate: Rate): Status {
  if (key === 'retry_success_rate') return 'none'
  const definition = KPIS.find((kpi) => kpi.key === key)!
  return metricTargetStatus(rate, definition.target, definition.up)
}

/** Also accepts Admin's objective-specific target overrides. */
export function metricTargetStatus(rate: Rate, target: number, up: boolean): Status {
  if (rate.value === null || rate.denominator === 0) return 'none'
  return (up ? rate.value >= target : rate.value <= target) ? 'met' : 'miss'
}

export function formatMetricValue(value: number | null, percent: boolean, empty = '—'): string {
  if (value === null) return empty
  return percent ? `${value}%` : value.toFixed(2)
}

export function formatKpi(key: EvidenceKey, rate: Rate): string {
  if (rate.value === null || rate.denominator === 0) return '—'
  return formatMetricValue(rate.value, key !== 'arc')
}
