/**
 * ⚠ DEV-ONLY DESIGN FIXTURES — never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/dashboard to
 * evaluate the redesign without auth or live API data.
 */
import type { DashboardSummary } from '@/features/dashboard/types'

export const previewPlayerName = 'riconalla'
export const previewGitcoins = 1240

/** Mid-tier player: Warden rank, 40+ quests, mixed retry history, 5 storeys, 12-day streak. */
export const richDashboardFixture: DashboardSummary = {
  kpis: {
    practice_completion: { value: 78, numerator: 32, denominator: 41 },
    scr: { value: 83, numerator: 39, denominator: 47 },
    arc: { value: 1.6, numerator: 74, denominator: 47 },
    car: { value: 91, numerator: 412, denominator: 453 },
    hlcr: { value: 62, numerator: 8, denominator: 13 },
    rta: { value: 70, numerator: 7, denominator: 10 },
  },
  storey_kpis: {
    '1': {
      scr: { value: 100, numerator: 9, denominator: 9 },
      hlcr: { value: 100, numerator: 3, denominator: 3 },
      rta: { value: 100, numerator: 2, denominator: 2 },
      arc: { value: 1.1, numerator: 10, denominator: 9 },
    },
    '2': {
      scr: { value: 92, numerator: 11, denominator: 12 },
      hlcr: { value: 75, numerator: 3, denominator: 4 },
      rta: { value: 67, numerator: 2, denominator: 3 },
      arc: { value: 1.4, numerator: 17, denominator: 12 },
    },
    '3': {
      scr: { value: 80, numerator: 8, denominator: 10 },
      hlcr: { value: 50, numerator: 1, denominator: 2 },
      rta: { value: 50, numerator: 1, denominator: 2 },
      arc: { value: 1.8, numerator: 18, denominator: 10 },
    },
    '4': {
      scr: { value: 70, numerator: 7, denominator: 10 },
      hlcr: { value: 33, numerator: 1, denominator: 3 },
      rta: { value: 67, numerator: 2, denominator: 3 },
      arc: { value: 2.1, numerator: 21, denominator: 10 },
    },
    '5': {
      scr: { value: 67, numerator: 4, denominator: 6 },
      hlcr: { value: null, numerator: 0, denominator: 1 },
      rta: { value: null, numerator: 0, denominator: 0 },
      arc: { value: 2.0, numerator: 8, denominator: 6 },
    },
  },
  counts: {
    started: 61,
    completed: 43,
    failed: 9,
    abandoned: 5,
    review_started: 12,
  },
  streak: {
    current: 12,
    longest: 19,
    last_completed_on: '2026-06-11',
  },
  first_attempt_stars: 26,
  retry_trends: [
    { practice_title: 'Rebase the Haunted Branch', attempts: 1, retries: 0, label: 'Storey 5 · Challenge · Hard' },
    { practice_title: 'Cherry-pick the Lost Relics', attempts: 3, retries: 2, label: 'Storey 4 · Challenge · Medium' },
    { practice_title: 'git stash — Vault of Half-Work', attempts: 1, retries: 0, label: 'Storey 4 · Adventure' },
    { practice_title: 'Merge of the Twin Towers', attempts: 6, retries: 5, label: 'Storey 4 · Challenge · Hard' },
    { practice_title: 'Detached HEAD in the Catacombs', attempts: 4, retries: 3, label: 'Storey 3 · Challenge · Medium' },
    { practice_title: 'git branch — Forking Paths', attempts: 2, retries: 1, label: 'Storey 3 · Adventure' },
    { practice_title: 'Amend the Royal Decree', attempts: 1, retries: 0, label: 'Storey 2 · Challenge · Easy' },
    { practice_title: 'Reset the Cursed Commit', attempts: 3, retries: 2, label: 'Storey 2 · Challenge · Medium' },
  ],
}

/** Brand-new account: everything null/zero — exercises the empty states. */
export const emptyDashboardFixture: DashboardSummary = {
  kpis: {
    practice_completion: { value: null, numerator: 0, denominator: 0 },
    scr: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
    car: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
    rta: { value: null, numerator: 0, denominator: 0 },
  },
  storey_kpis: {},
  counts: { started: 0, completed: 0, failed: 0, abandoned: 0, review_started: 0 },
  streak: { current: 0, longest: 0, last_completed_on: null },
  first_attempt_stars: 0,
  retry_trends: [],
}
