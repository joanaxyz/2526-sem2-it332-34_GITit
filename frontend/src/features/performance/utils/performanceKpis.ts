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
    key: 'scr', label: 'Tiers mastered',
    explanation: 'Required tiers where you completed every successful repetition, however many attempts you needed.',
    scope: 'Modules 1–4 · required tiers with an outcome',
    emptyHint: 'Finish or fail a run on a required tier to begin your mastery record.',
    abbr: 'SCR', name: 'Scenario Completion Rate', target: 80, up: true, pct: true,
    formula: 'Required tiers mastered ÷ Unique required tiers attempted × 100',
    why: 'Measures eventual mastery. A tier counts as attempted once a run on it ends, or its commands sit idle for 7 days; opening a tier is not an attempt. Formal studies use fixed assigned tiers, including unattempted tiers, as the denominator.',
  },
  {
    key: 'car', label: 'Command efficiency',
    explanation: 'Command use compared with a validated solution, from your latest clear of each scenario on a variant you had not solved before. Replays that meet new variants can raise it; repeating a solved variant never counts. Incorrect commands consume the same budget; optional diagnostics are free.',
    scope: 'Modules 1–4 · latest fresh clear per scenario',
    emptyHint: 'Clear a scenario with a validated command reference. Older runs without reference evidence remain unscored.',
    abbr: 'CAR', name: 'Command Accuracy Rate', target: 70, up: true, pct: true,
    formula: 'Mean over scenarios of 100 × min(1, T ÷ max(1, A))',
    why: 'Let T = validated reference commands and A = commands used on the scenario’s latest clear of content you had not cleared before. This official KPI measures reference-relative efficiency on new problems, so practice shows without rewarding memorized answers. Scores are capped at 100%.',
  },
  {
    key: 'hlcr', label: 'Hard tiers mastered',
    explanation: 'Hard required tiers where you completed every required successful repetition.',
    scope: 'Modules 1–4 · hard tiers with an outcome',
    emptyHint: 'Try a hard required tier when you are ready.',
    abbr: 'HLCR', name: 'Hard-Level Completion Rate', target: 70, up: true, pct: true,
    formula: 'Required hard tiers mastered ÷ Unique required hard tiers attempted × 100',
    why: 'Measures hard-task mastery, counting attempts as SCR does. Formal studies use assigned hard tiers. Module 4 retains its approved 65% objective target.',
  },
  {
    key: 'arc', label: 'Retries before mastery',
    explanation: 'Failed attempts and attempts you left after submitting commands, before each mastered tier. Successful required repetitions are not retries.',
    scope: 'Modules 1–4 · mastered tiers only',
    emptyHint: 'Master a required tier to see your retry average.',
    abbr: 'ARC', name: 'Avg Retry Count', longName: 'Average Retry Count',
    target: 2, up: false, pct: false,
    formula: 'Unsuccessful attempts before mastery ÷ Tiers mastered',
    why: 'Shows unsuccessful attempts needed for mastery. The contributing tier count matters; Module 4 retains its approved maximum of 3.',
  },
  {
    key: 'rta', label: 'Transfer checkpoints cleared',
    explanation: 'Your first attempt on a reserved unfamiliar repository or goal, after practice. Its first result is preserved even if you practice again.',
    scope: 'Modules 3–4 · reserved unseen transfer checkpoints',
    emptyHint: 'Measured on unseen transfer checkpoints in Modules 3–4. Requires reserved content and complete exposure evidence.',
    abbr: 'RTA', name: 'Retry Transfer Accuracy', target: 65, up: true, pct: true,
    formula: 'Novel checkpoints cleared on first run ÷ Novel checkpoints assessed × 100',
    why: 'Measures transfer after practice, including learners who never failed. Formal studies include all assigned valid checkpoints at cutoff; unavailable novelty evidence is missing.',
    tooltip: 'A content-author review and durable exposure history establish novelty. A different variant ID alone is insufficient.',
  },
] as const satisfies readonly { key: Exclude<keyof ApiSchemas['PerformanceKpiSet'], 'retry_success_rate' | 'rtr'>; [field: string]: unknown }[]

export type KpiKey = (typeof KPIS)[number]['key']

/** The old RTR measure, shown next to the evaluation KPIs for context. It has
 * no target, so it never counts toward "targets met". */
export const SUPPLEMENTARY_KPI = {
  key: 'retry_success_rate', label: 'Retry recovery',
  explanation: 'Concluded retries following an actual failed run that succeed.',
  scope: 'Modules 1–4 · for context, no target',
  emptyHint: 'Measured once a retry following an unsuccessful attempt ends.',
  formula: 'Successful recovery retries ÷ Concluded recovery retries × 100',
  abbr: 'RSR', name: 'Retry Success Rate (supplementary)', pct: true,
  tooltip: 'Successful required repetitions are not recovery retries. Transfer is measured separately.',
} as const

/** Any card on the Overall row: an evaluation KPI (with a target) or the
 * supplementary indicator (without one). */
export type CardKpi = (typeof KPIS)[number] | typeof SUPPLEMENTARY_KPI

export const EMPTY_RATE: Rate = { value: null, numerator: 0, denominator: 0 }

export function getModuleRate(mod: PerformanceModule, key: KpiKey): Rate {
  if (key === 'scr') return mod.scr
  if (key === 'car') return mod.car
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
  scr: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'required tier', 'required tiers')} mastered`,
    none: 'No attempted required tiers yet',
  },
  car: {
    some: (n, d) => `${n.toLocaleString()} score points across ${counted(d, 'scored scenario', 'scored scenarios')}`,
    none: 'No scored scenarios yet',
  },
  hlcr: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'hard tier', 'hard tiers')} mastered`,
    none: 'No attempted hard tiers yet',
  },
  arc: {
    some: (n, d) => `${counted(n, 'unsuccessful attempt', 'unsuccessful attempts')} across ${counted(d, 'mastered tier', 'mastered tiers')}`,
    none: 'No mastered tiers yet',
  },
  rta: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'transfer checkpoint', 'transfer checkpoints')} cleared first time`,
    none: 'No assessed transfer checkpoints yet',
  },
  retry_success_rate: {
    some: (n, d) => `${n.toLocaleString()} of ${counted(d, 'recovery retry', 'recovery retries')} succeeded`,
    none: 'No concluded recovery retries yet',
  },
}

export function kpiEvidence(key: EvidenceKey, rate: Rate) {
  if (rate.unit === 'participants' && rate.denominator > 0) return `${counted(rate.denominator, 'contributing learner', 'contributing learners')} · equally weighted`
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

/** CAR's starting point, from each scenario's first fresh clear; null until measured. */
export function carStartingPoint(first: Rate | undefined): string | null {
  if (!first || first.value === null || first.denominator === 0) return null
  return `Started at ${formatMetricValue(first.value, true)}`
}

export function formatKpi(key: EvidenceKey, rate: Rate): string {
  if (rate.value === null || rate.denominator === 0) return '—'
  return formatMetricValue(rate.value, key !== 'arc')
}
