/**
 * DEV-ONLY DESIGN FIXTURES - never imported by production routes.
 *
 * The Overview's module band fetches its own summary, so without these the
 * design preview could only ever show that band's error state.
 */
import type { PerformanceSummary } from '@/features/performance/types'

/** Mirrors the rich home preview player: strong early modules, thin late ones. */
export const richPerformanceFixture: PerformanceSummary = {
  completed_sessions: 43,
  kpis: {
    scr: { value: 76, numerator: 43, denominator: 57 },
    car: { value: 91, numerator: 1080, denominator: 1187 },
    hlcr: { value: 62, numerator: 8, denominator: 13 },
    rtr: { value: 58, numerator: 11, denominator: 19 },
    arc: { value: 1.6, numerator: 74, denominator: 47 },
  },
  modules: [
    {
      number: 0,
      title: 'Module 0',
      scr: { value: 100, numerator: 3, denominator: 3 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rtr: { value: null, numerator: 0, denominator: 0 },
      arc: { value: 1, numerator: 3, denominator: 3 },
    },
    {
      number: 1,
      title: 'Repository Foundations',
      scr: { value: 100, numerator: 11, denominator: 11 },
      hlcr: { value: 100, numerator: 3, denominator: 3 },
      rtr: { value: 80, numerator: 4, denominator: 5 },
      arc: { value: 1.18, numerator: 13, denominator: 11 },
    },
    {
      number: 2,
      title: 'Branching Basics',
      scr: { value: 78, numerator: 7, denominator: 9 },
      hlcr: { value: 67, numerator: 2, denominator: 3 },
      rtr: { value: 60, numerator: 3, denominator: 5 },
      arc: { value: 1.71, numerator: 12, denominator: 7 },
    },
    {
      number: 3,
      title: 'Merging & Conflicts',
      scr: { value: 45, numerator: 5, denominator: 11 },
      hlcr: { value: 33, numerator: 1, denominator: 3 },
      rtr: { value: 44, numerator: 4, denominator: 9 },
      arc: { value: 2.4, numerator: 12, denominator: 5 },
    },
    {
      number: 4,
      title: 'Remote Work',
      scr: { value: null, numerator: 0, denominator: 0 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rtr: { value: null, numerator: 0, denominator: 0 },
      arc: { value: null, numerator: 0, denominator: 0 },
    },
  ],
}

/** Brand-new account: the module band's own empty state. */
export const emptyPerformanceFixture: PerformanceSummary = {
  completed_sessions: 0,
  kpis: {
    scr: { value: null, numerator: 0, denominator: 0 },
    car: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
    rtr: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
  },
  modules: [1, 2, 3, 4].map((number) => ({
    number,
    title: `Module ${number}`,
    scr: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
    rtr: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
  })),
}
