/** DEV-ONLY fixtures for the real Home preview. Counts aggregate across Modules 1–4. */
import type { PerformanceSummary } from '@/features/performance/types'
import { MODULES } from '@/features/performance/utils/learningObjectives'

export const richPerformanceFixture: PerformanceSummary = {
  completed_sessions: 43,
  samples: { participants: 1, attempted_tiers: 57, in_progress_tiers: 0, mastered_tiers: 43, mastery_missing: 0, car_scored: 43, car_missing: 0, transfer_assigned: 5, transfer_pending: 0, transfer_missing: 0 },
  objectives: Object.fromEntries(MODULES.flatMap((module) => module.sos
    .filter((objective) => objective.metrics.some((metric) => metric.kpi === 'car'))
    .map((objective) => [objective.id, { value: 91, numerator: 91, denominator: 1 }]))),
  transfers: [],
  kpis: {
    scr: { value: 75.4, numerator: 43, denominator: 57 },
    car: { value: 91, numerator: 3913, denominator: 43 },
    car_first: { value: 78, numerator: 3354, denominator: 43 },
    hlcr: { value: 61.5, numerator: 8, denominator: 13 },
    rta: { value: 60, numerator: 3, denominator: 5 },
    retry_success_rate: { value: 63.6, numerator: 21, denominator: 33 },
    arc: { value: 1.6, numerator: 69, denominator: 43 },
  },
  modules: [
    {
      car: { value: 91, numerator: 91, denominator: 1 },
      car_first: { value: 76, numerator: 76, denominator: 1 },
      number: 1, title: 'Local Repository Foundations',
      scr: { value: 100, numerator: 11, denominator: 11 },
      hlcr: { value: 100, numerator: 3, denominator: 3 },
      rta: { value: null, numerator: 0, denominator: 0 },
      retry_success_rate: { value: 83.3, numerator: 5, denominator: 6 },
      arc: { value: 1.18, numerator: 13, denominator: 11 },
    },
    {
      car: { value: 91, numerator: 91, denominator: 1 },
      car_first: { value: 76, numerator: 76, denominator: 1 },
      number: 2, title: 'Branching and Collaboration',
      scr: { value: 77.8, numerator: 14, denominator: 18 },
      hlcr: { value: 66.7, numerator: 2, denominator: 3 },
      rta: { value: null, numerator: 0, denominator: 0 },
      retry_success_rate: { value: 60, numerator: 6, denominator: 10 },
      arc: { value: 1.71, numerator: 24, denominator: 14 },
    },
    {
      car: { value: 91, numerator: 91, denominator: 1 },
      car_first: { value: 76, numerator: 76, denominator: 1 },
      number: 3, title: 'Conflict Resolution',
      scr: { value: 50, numerator: 10, denominator: 20 },
      hlcr: { value: 33.3, numerator: 1, denominator: 3 },
      rta: { value: 33.3, numerator: 1, denominator: 3 },
      retry_success_rate: { value: 50, numerator: 6, denominator: 12 },
      arc: { value: 2.4, numerator: 24, denominator: 10 },
    },
    {
      car: { value: 91, numerator: 91, denominator: 1 },
      car_first: { value: 76, numerator: 76, denominator: 1 },
      number: 4, title: 'Advanced Recovery and History',
      scr: { value: 100, numerator: 8, denominator: 8 },
      hlcr: { value: 50, numerator: 2, denominator: 4 },
      rta: { value: 100, numerator: 2, denominator: 2 },
      retry_success_rate: { value: 80, numerator: 4, denominator: 5 },
      arc: { value: 1, numerator: 8, denominator: 8 },
    },
  ],
}

/** Brand-new account: the module band's own empty state. */
export const emptyPerformanceFixture: PerformanceSummary = {
  completed_sessions: 0,
  samples: { participants: 1, attempted_tiers: 0, in_progress_tiers: 0, mastered_tiers: 0, mastery_missing: 0, car_scored: 0, car_missing: 0, transfer_assigned: 0, transfer_pending: 0, transfer_missing: 0 },
  objectives: Object.fromEntries(Object.keys(richPerformanceFixture.objectives)
    .map((id) => [id, { value: null, numerator: 0, denominator: 0 }])),
  transfers: [],
  kpis: {
    scr: { value: null, numerator: 0, denominator: 0 },
    car: { value: null, numerator: 0, denominator: 0 },
    car_first: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
    rta: { value: null, numerator: 0, denominator: 0 },
    retry_success_rate: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
  },
  modules: [1, 2, 3, 4].map((number) => ({
    number,
    title: `Module ${number}`,
    car: { value: null, numerator: 0, denominator: 0 },
    car_first: { value: null, numerator: 0, denominator: 0 },
    scr: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
    rta: { value: null, numerator: 0, denominator: 0 },
    retry_success_rate: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
  })),
}
