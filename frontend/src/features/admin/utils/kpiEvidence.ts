import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type Rate = ApiSchemas['RateMetric']

export type EvidenceKey = 'scr' | 'car' | 'hlcr' | 'arc' | 'rta' | 'retry_success_rate'

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
