/**
 * DEV-ONLY DESIGN FIXTURES - never imported by production routes.
 * Realistic mid-progress player data used by /design-preview/home.
 */
import type { StatsSummary } from '@/features/stats/types'
import type { ActivityWindow } from '@/features/stats/utils/activityWindow'

/** Mirrors the home preview player: 43 levels, 12-day streak, 1240 coins. */
export const richStatsFixture: StatsSummary = {
  skill_profile: [
    { key: 'git-init', label: 'git init', hint: 'Create Git metadata in the current directory or a named directory.', value: 100, command: 'git init' },
    { key: 'git-clone', label: 'git clone', hint: 'Create a local repository from a remote URL and optionally choose branch, depth, or folder.', value: 92, command: 'git clone' },
    { key: 'git-log', label: 'git log', hint: 'Inspect commit history and branch shape.', value: 88, command: 'git log' },
    { key: 'git-show', label: 'git show', hint: 'Inspect the latest commit or a named object without changing repository state.', value: 74, command: 'git show' },
    { key: 'git-add', label: 'git add', hint: 'Copy selected working directory changes into the staging area.', value: 96, command: 'git add' },
    { key: 'git-commit', label: 'git commit', hint: 'Create or replace a commit from the staged snapshot.', value: 90, command: 'git commit' },
    { key: 'git-restore', label: 'git restore', hint: 'Discard working-tree changes or move staged changes back to the working directory.', value: 61, command: 'git restore' },
    { key: 'git-branch', label: 'git branch', hint: 'Inspect, create, and delete branch pointers while keeping HEAD where it is.', value: 68, command: 'git branch' },
    { key: 'git-switch', label: 'git switch', hint: 'Move HEAD to another branch, or create and switch in one safe step.', value: 55, command: 'git switch' },
    { key: 'git-merge', label: 'git merge', hint: 'Combine another branch into the current branch, or manage an in-progress merge.', value: 47, command: 'git merge' },
    { key: 'git-revert', label: 'git revert', hint: 'Create a new commit that reverses an older commit without deleting shared history.', value: 33, command: 'git revert' },
    { key: 'git-reflog', label: 'git reflog', hint: 'Inspect recent HEAD movements for recovery clues.', value: 20, command: 'git reflog' },
    { key: 'git-stash', label: 'git stash', hint: 'Temporarily shelve local work and restore it later.', value: 28, command: 'git stash' },
    { key: 'git-cherry-pick', label: 'git cherry-pick', hint: 'Apply one existing commit onto the current branch.', value: 12, command: 'git cherry-pick' },
    { key: 'git-fetch', label: 'git fetch', hint: 'Update remote-tracking branches without changing local work.', value: 35, command: 'git fetch' },
    { key: 'git-pull', label: 'git pull', hint: 'Fetch and integrate upstream changes into the current branch.', value: 24, command: 'git pull' },
    { key: 'git-push', label: 'git push', hint: 'Publish local commits, set upstream tracking, force with lease, or delete remote branches.', value: 41, command: 'git push' },
    { key: 'git-rebase', label: 'git rebase', hint: 'Replay commits onto another base to keep history linear.', value: 0, command: 'git rebase' },
  ],
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
    { key: 'git-init', label: 'git init', hint: 'Create Git metadata in the current directory or a named directory.', value: null, command: 'git init' },
    { key: 'git-clone', label: 'git clone', hint: 'Create a local repository from a remote URL and optionally choose branch, depth, or folder.', value: null, command: 'git clone' },
    { key: 'git-log', label: 'git log', hint: 'Inspect commit history and branch shape.', value: null, command: 'git log' },
    { key: 'git-show', label: 'git show', hint: 'Inspect the latest commit or a named object without changing repository state.', value: null, command: 'git show' },
    { key: 'git-add', label: 'git add', hint: 'Copy selected working directory changes into the staging area.', value: null, command: 'git add' },
    { key: 'git-commit', label: 'git commit', hint: 'Create or replace a commit from the staged snapshot.', value: null, command: 'git commit' },
    { key: 'git-restore', label: 'git restore', hint: 'Discard working-tree changes or move staged changes back to the working directory.', value: null, command: 'git restore' },
    { key: 'git-branch', label: 'git branch', hint: 'Inspect, create, and delete branch pointers while keeping HEAD where it is.', value: null, command: 'git branch' },
    { key: 'git-switch', label: 'git switch', hint: 'Move HEAD to another branch, or create and switch in one safe step.', value: null, command: 'git switch' },
    { key: 'git-merge', label: 'git merge', hint: 'Combine another branch into the current branch, or manage an in-progress merge.', value: null, command: 'git merge' },
    { key: 'git-revert', label: 'git revert', hint: 'Create a new commit that reverses an older commit without deleting shared history.', value: null, command: 'git revert' },
    { key: 'git-reflog', label: 'git reflog', hint: 'Inspect recent HEAD movements for recovery clues.', value: null, command: 'git reflog' },
    { key: 'git-stash', label: 'git stash', hint: 'Temporarily shelve local work and restore it later.', value: null, command: 'git stash' },
    { key: 'git-cherry-pick', label: 'git cherry-pick', hint: 'Apply one existing commit onto the current branch.', value: null, command: 'git cherry-pick' },
    { key: 'git-fetch', label: 'git fetch', hint: 'Update remote-tracking branches without changing local work.', value: null, command: 'git fetch' },
    { key: 'git-pull', label: 'git pull', hint: 'Fetch and integrate upstream changes into the current branch.', value: null, command: 'git pull' },
    { key: 'git-push', label: 'git push', hint: 'Publish local commits, set upstream tracking, force with lease, or delete remote branches.', value: null, command: 'git push' },
    { key: 'git-rebase', label: 'git rebase', hint: 'Replay commits onto another base to keep history linear.', value: null, command: 'git rebase' },
  ],
  activity_window: 'month',
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
