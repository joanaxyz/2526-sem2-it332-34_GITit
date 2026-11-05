/**
 * DEV-ONLY DESIGN FIXTURES - never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/home.
 */
import type { StatsSummary } from '@/features/stats/types'
import type { ActivityWindow } from '@/features/stats/utils/activityWindow'

/** Mirrors the home preview player: 43 levels, 5 gate trials, 1240 coins. */
export const richStatsFixture: StatsSummary = {
  activity_window: 'month',
  activity_trend: [
    { date: '2026-05-15', levels_completed: 0, commands_run: 0 },
    { date: '2026-05-16', levels_completed: 1, commands_run: 18 },
    { date: '2026-05-17', levels_completed: 0, commands_run: 0 },
    { date: '2026-05-18', levels_completed: 2, commands_run: 34 },
    { date: '2026-05-19', levels_completed: 1, commands_run: 27 },
    { date: '2026-05-20', levels_completed: 3, commands_run: 46 },
    { date: '2026-05-21', levels_completed: 0, commands_run: 12 },
    { date: '2026-05-22', levels_completed: 2, commands_run: 31 },
    { date: '2026-05-23', levels_completed: 0, commands_run: 0 },
    { date: '2026-05-24', levels_completed: 1, commands_run: 23 },
    { date: '2026-05-25', levels_completed: 2, commands_run: 40 },
    { date: '2026-05-26', levels_completed: 3, commands_run: 55 },
    { date: '2026-05-27', levels_completed: 1, commands_run: 19 },
    { date: '2026-05-28', levels_completed: 2, commands_run: 36 },
    { date: '2026-05-29', levels_completed: 2, commands_run: 38 },
    { date: '2026-05-30', levels_completed: 1, commands_run: 22 },
    { date: '2026-05-31', levels_completed: 3, commands_run: 51 },
    { date: '2026-06-01', levels_completed: 2, commands_run: 44 },
    { date: '2026-06-02', levels_completed: 0, commands_run: 9 },
    { date: '2026-06-03', levels_completed: 4, commands_run: 67 },
    { date: '2026-06-04', levels_completed: 2, commands_run: 41 },
    { date: '2026-06-05', levels_completed: 3, commands_run: 58 },
    { date: '2026-06-06', levels_completed: 1, commands_run: 26 },
    { date: '2026-06-07', levels_completed: 4, commands_run: 72 },
    { date: '2026-06-08', levels_completed: 2, commands_run: 39 },
    { date: '2026-06-09', levels_completed: 5, commands_run: 84 },
    { date: '2026-06-10', levels_completed: 3, commands_run: 55 },
    { date: '2026-06-11', levels_completed: 2, commands_run: 47 },
    { date: '2026-06-12', levels_completed: 1, commands_run: 29 },
    { date: '2026-06-13', levels_completed: 3, commands_run: 61 },
  ],
  headline: {
    levels_completed: 43,
    finish_rate: { value: 76, numerator: 43, denominator: 57 },
    accuracy: 91,
    hard_tier_clears: { value: 4, scope: 'hard challenges beaten' },
    comebacks: { value: 6, scope: 'retries turned into wins' },
    perfect_clears: 12,
    gate_trial_clears: 5,
    hard_gate_trial_clears: 1,
    gitcoins: 1240,
    gitcoins_earned: 2165,
    commands_run: 1187,
  },
}

/** Brand-new account: everything null/zero - exercises the empty states. */
export const emptyStatsFixture: StatsSummary = {
  activity_window: 'month',
  activity_trend: [],
  headline: {
    levels_completed: 0,
    finish_rate: { value: null, numerator: 0, denominator: 0 },
    accuracy: null,
    hard_tier_clears: { value: 0, scope: 'hard challenges beaten' },
    comebacks: { value: 0, scope: 'retries turned into wins' },
    perfect_clears: 0,
    gate_trial_clears: 0,
    hard_gate_trial_clears: 0,
    gitcoins: 0,
    gitcoins_earned: 0,
    commands_run: 0,
  },
}

/**
 * The rich player's trend re-cut for a chosen span, so the preview's Week /
 * Month / Year control actually moves the plot instead of pending forever.
 * Week is the tail of the month; Year sums each month into one point.
 */
export function richStatsFixtureFor(window: ActivityWindow): StatsSummary {
  if (window === 'month') return richStatsFixture
  if (window === 'week') {
    return { ...richStatsFixture, activity_window: 'week', activity_trend: richStatsFixture.activity_trend.slice(-7) }
  }
  const months = [
    { date: '2025-07-01', levels_completed: 0, commands_run: 0 },
    { date: '2025-08-01', levels_completed: 2, commands_run: 61 },
    { date: '2025-09-01', levels_completed: 5, commands_run: 148 },
    { date: '2025-10-01', levels_completed: 3, commands_run: 96 },
    { date: '2025-11-01', levels_completed: 0, commands_run: 0 },
    { date: '2025-12-01', levels_completed: 1, commands_run: 34 },
    { date: '2026-01-01', levels_completed: 6, commands_run: 187 },
    { date: '2026-02-01', levels_completed: 4, commands_run: 121 },
    { date: '2026-03-01', levels_completed: 2, commands_run: 74 },
    { date: '2026-04-01', levels_completed: 5, commands_run: 163 },
    { date: '2026-05-01', levels_completed: 9, commands_run: 329 },
    { date: '2026-06-01', levels_completed: 6, commands_run: 424 },
  ]
  return { ...richStatsFixture, activity_window: 'year', activity_trend: months }
}
