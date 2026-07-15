/**
 * DEV-ONLY DESIGN FIXTURES - never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/home to
 * evaluate the hub without auth or live API data.
 */
import type { HomeSummary } from '@/features/home/types'

export const previewPlayerName = 'Learner'
export const previewGitcoins = 1240

/** Mid-tier player: Warden rank, 40+ levels, mixed retry history, 5 chapters, 12-day streak. */
export const richHomeFixture: HomeSummary = {
  kpis: {
    scr: { value: 83, numerator: 39, denominator: 47 },
    arc: { value: 1.6, numerator: 74, denominator: 47 },
    hlcr: { value: 62, numerator: 8, denominator: 13 },
  },
  chapter_kpis: {
    '1': {
      scr: { value: 100, numerator: 9, denominator: 9 },
      hlcr: { value: 100, numerator: 3, denominator: 3 },
      arc: { value: 1.1, numerator: 10, denominator: 9 },
    },
    '2': {
      scr: { value: 92, numerator: 11, denominator: 12 },
      hlcr: { value: 75, numerator: 3, denominator: 4 },
      arc: { value: 1.4, numerator: 17, denominator: 12 },
    },
    '3': {
      scr: { value: 80, numerator: 8, denominator: 10 },
      hlcr: { value: 50, numerator: 1, denominator: 2 },
      arc: { value: 1.8, numerator: 18, denominator: 10 },
    },
    '4': {
      scr: { value: 70, numerator: 7, denominator: 10 },
      hlcr: { value: 33, numerator: 1, denominator: 3 },
      arc: { value: 2.1, numerator: 21, denominator: 10 },
    },
    '5': {
      scr: { value: 67, numerator: 4, denominator: 6 },
      hlcr: { value: null, numerator: 0, denominator: 1 },
      arc: { value: 2.0, numerator: 8, denominator: 6 },
    },
  },
  counts: {
    started: 61,
    completed: 43,
    failed: 9,
    abandoned: 5,
  },
  streak: {
    current: 12,
    longest: 19,
    last_completed_on: '2026-06-11',
  },
  perfect_clears: 26,
  mastery: 68,
  retry_trends: [
    { level_title: 'Rebase the Haunted Branch', attempts: 1, retries: 0, label: 'Chapter 5 - Challenge - Hard' },
    { level_title: 'Cherry-pick the Lost Relics', attempts: 3, retries: 2, label: 'Chapter 4 - Challenge - Medium' },
    { level_title: 'git stash - Vault of Half-Work', attempts: 1, retries: 0, label: 'Chapter 4 - Adventure' },
    { level_title: 'Merge of the Twin Branches', attempts: 6, retries: 5, label: 'Chapter 4 - Challenge - Hard' },
    { level_title: 'Detached HEAD in the Catacombs', attempts: 4, retries: 3, label: 'Chapter 3 - Challenge - Medium' },
    { level_title: 'git branch - Forking Paths', attempts: 2, retries: 1, label: 'Chapter 3 - Adventure' },
    { level_title: 'Amend the Royal Decree', attempts: 1, retries: 0, label: 'Chapter 2 - Challenge - Easy' },
    { level_title: 'Reset the Cursed Commit', attempts: 3, retries: 2, label: 'Chapter 2 - Challenge - Medium' },
  ],
}

/** Brand-new account: everything null/zero - exercises the empty states. */
export const emptyHomeFixture: HomeSummary = {
  kpis: {
    scr: { value: null, numerator: 0, denominator: 0 },
    arc: { value: null, numerator: 0, denominator: 0 },
    hlcr: { value: null, numerator: 0, denominator: 0 },
  },
  chapter_kpis: {},
  counts: { started: 0, completed: 0, failed: 0, abandoned: 0 },
  streak: { current: 0, longest: 0, last_completed_on: null },
  perfect_clears: 0,
  mastery: 0,
  retry_trends: [],
}
