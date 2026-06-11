/**
 * ⚠ DEV-ONLY DESIGN FIXTURES — never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/stats.
 */
import type { StatsSummary } from '@/features/stats/types'

/** Mirrors the dashboard preview player: 43 quests, 12-day streak, 1240 coins. */
export const richStatsFixture: StatsSummary = {
  skill_profile: [
    { key: 'accuracy', label: 'Accuracy', hint: 'How often your commands are accepted first time', value: 91 },
    { key: 'efficiency', label: 'Efficiency', hint: 'Solving quests without wasted commands', value: 74 },
    { key: 'independence', label: 'Independence', hint: 'Clearing quests without hints or retries', value: 62 },
    { key: 'consistency', label: 'Consistency', hint: 'Showing up and finishing what you start', value: 84 },
    { key: 'mastery', label: 'Mastery', hint: 'Success on hard, boss-level challenges', value: 58 },
    { key: 'coverage', label: 'Coverage', hint: 'Breadth of git commands you have used', value: 69 },
  ],
  activity_trend: [
    { date: '2026-05-29', problems_completed: 2, commands_run: 38 },
    { date: '2026-05-30', problems_completed: 1, commands_run: 22 },
    { date: '2026-05-31', problems_completed: 3, commands_run: 51 },
    { date: '2026-06-01', problems_completed: 2, commands_run: 44 },
    { date: '2026-06-02', problems_completed: 0, commands_run: 9 },
    { date: '2026-06-03', problems_completed: 4, commands_run: 67 },
    { date: '2026-06-04', problems_completed: 2, commands_run: 41 },
    { date: '2026-06-05', problems_completed: 3, commands_run: 58 },
    { date: '2026-06-06', problems_completed: 1, commands_run: 26 },
    { date: '2026-06-07', problems_completed: 4, commands_run: 72 },
    { date: '2026-06-08', problems_completed: 2, commands_run: 39 },
    { date: '2026-06-09', problems_completed: 5, commands_run: 84 },
    { date: '2026-06-10', problems_completed: 3, commands_run: 55 },
    { date: '2026-06-11', problems_completed: 2, commands_run: 47 },
  ],
  headline: {
    quests_completed: 43,
    finish_rate: { value: 76, numerator: 43, denominator: 57 },
    accuracy: 91,
    boss_floors: { value: 4, scope: 'hard challenges beaten' },
    comebacks: { value: 6, scope: 'retries turned into wins' },
    perfect_clears: 12,
    day_streak: 12,
    longest_streak: 19,
    gitcoins: 1240,
    commands_run: 1187,
  },
}

/** Brand-new account: everything null/zero — exercises the empty states. */
export const emptyStatsFixture: StatsSummary = {
  skill_profile: [
    { key: 'accuracy', label: 'Accuracy', hint: 'How often your commands are accepted first time', value: null },
    { key: 'efficiency', label: 'Efficiency', hint: 'Solving quests without wasted commands', value: null },
    { key: 'independence', label: 'Independence', hint: 'Clearing quests without hints or retries', value: null },
    { key: 'consistency', label: 'Consistency', hint: 'Showing up and finishing what you start', value: null },
    { key: 'mastery', label: 'Mastery', hint: 'Success on hard, boss-level challenges', value: null },
    { key: 'coverage', label: 'Coverage', hint: 'Breadth of git commands you have used', value: null },
  ],
  activity_trend: [],
  headline: {
    quests_completed: 0,
    finish_rate: { value: null, numerator: 0, denominator: 0 },
    accuracy: null,
    boss_floors: { value: 0, scope: 'hard challenges beaten' },
    comebacks: { value: 0, scope: 'retries turned into wins' },
    perfect_clears: 0,
    day_streak: 0,
    longest_streak: 0,
    gitcoins: 0,
    commands_run: 0,
  },
}
