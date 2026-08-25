/**
 * DEV-ONLY DESIGN FIXTURES - never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/home.
 */
import type { StatsSummary } from '@/features/stats/types'

/** Mirrors the home preview player: 43 levels, 12-day streak, 1240 coins. */
export const richStatsFixture: StatsSummary = {
  skill_profile: [
    { key: 'git-init', label: 'Initialize', hint: 'Mastery of git init', value: 100, command: 'git init' },
    { key: 'git-status', label: 'Status', hint: 'Mastery of git status', value: 95, command: 'git status' },
    { key: 'git-add', label: 'Stage Changes', hint: 'Mastery of git add', value: 88, command: 'git add' },
    { key: 'git-commit', label: 'Commit', hint: 'Mastery of git commit', value: 82, command: 'git commit' },
    { key: 'git-log', label: 'History', hint: 'Mastery of git log', value: 74, command: 'git log' },
    { key: 'git-diff', label: 'Diff', hint: 'Mastery of git diff', value: 68, command: 'git diff' },
    { key: 'git-branch', label: 'Branching', hint: 'Mastery of git branch', value: 62, command: 'git branch' },
    { key: 'git-checkout', label: 'Checkout', hint: 'Mastery of git checkout', value: 55, command: 'git checkout' },
    { key: 'git-merge', label: 'Merge', hint: 'Mastery of git merge', value: 40, command: 'git merge' },
    { key: 'git-push', label: 'Push', hint: 'Mastery of git push', value: 30, command: 'git push' },
    { key: 'git-pull', label: 'Pull', hint: 'Mastery of git pull', value: 20, command: 'git pull' },
    { key: 'git-rebase', label: 'Rebase', hint: 'Mastery of git rebase', value: 0, command: 'git rebase' },
  ],
  activity_trend: [
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
  ],
  headline: {
    levels_completed: 43,
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

/** Brand-new account: everything null/zero - exercises the empty states. */
export const emptyStatsFixture: StatsSummary = {
  skill_profile: [
    { key: 'git-init', label: 'Initialize', hint: 'Mastery of git init', value: null, command: 'git init' },
    { key: 'git-status', label: 'Status', hint: 'Mastery of git status', value: null, command: 'git status' },
    { key: 'git-add', label: 'Stage Changes', hint: 'Mastery of git add', value: null, command: 'git add' },
    { key: 'git-commit', label: 'Commit', hint: 'Mastery of git commit', value: null, command: 'git commit' },
    { key: 'git-log', label: 'History', hint: 'Mastery of git log', value: null, command: 'git log' },
    { key: 'git-diff', label: 'Diff', hint: 'Mastery of git diff', value: null, command: 'git diff' },
    { key: 'git-branch', label: 'Branching', hint: 'Mastery of git branch', value: null, command: 'git branch' },
    { key: 'git-checkout', label: 'Checkout', hint: 'Mastery of git checkout', value: null, command: 'git checkout' },
    { key: 'git-merge', label: 'Merge', hint: 'Mastery of git merge', value: null, command: 'git merge' },
    { key: 'git-push', label: 'Push', hint: 'Mastery of git push', value: null, command: 'git push' },
    { key: 'git-pull', label: 'Pull', hint: 'Mastery of git pull', value: null, command: 'git pull' },
    { key: 'git-rebase', label: 'Rebase', hint: 'Mastery of git rebase', value: null, command: 'git rebase' },
  ],
  activity_trend: [],
  headline: {
    levels_completed: 0,
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
