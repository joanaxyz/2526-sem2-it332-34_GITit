import type { CSSProperties } from 'react'

import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'
import type { ChestReward, LearningStorey } from '@/features/tower-map/types'

// Per-difficulty label + accent (RGB triplet consumed via `rgba(var(--), )`).
export const DIFFICULTY_ACCENT: Record<string, { label: string; rgb: string }> = {
  easy: { label: 'Easy', rgb: '0, 245, 212' },
  medium: { label: 'Medium', rgb: '53, 143, 255' },
  hard: { label: 'Hard', rgb: '176, 74, 255' },
}

// Fallback while the API has no chest config; mirrors the backend defaults.
export const DEFAULT_CHEST_REWARDS: ChestReward[] = [
  { threshold: 25, coins: 25 },
  { threshold: 50, coins: 60 },
  { threshold: 75, coins: 100 },
  { threshold: 100, coins: 150 },
]

export function chestRewards(storey: Pick<LearningStorey, 'chest_rewards'>): ChestReward[] {
  return storey.chest_rewards?.length ? storey.chest_rewards : DEFAULT_CHEST_REWARDS
}

export function nextReward(rewards: ChestReward[], progress: number) {
  return rewards.find((chest) => progress < chest.threshold) ?? rewards[rewards.length - 1]
}

export function adventureActionLabel(adventure: CommandAdventureSummary) {
  if (adventure.status === 'completed') return 'Replay'
  if (adventure.active_run_id) return 'Resume'
  if (adventure.latest_run_id) return 'Replay'
  return 'Play'
}

export function difficultyLabel(level: ChallengeLevelAccess) {
  return DIFFICULTY_ACCENT[String(level.difficulty)]?.label ?? String(level.difficulty)
}

export function accuracyLabel(level: ChallengeLevelAccess | null) {
  const accuracy = level?.latest_attempt?.accuracy_rate
  return accuracy !== null && accuracy !== undefined ? `${accuracy}%` : '--%'
}

export function challengeLevelAccent(level: ChallengeLevelAccess | null) {
  if (!level) return DIFFICULTY_ACCENT.hard.rgb
  return DIFFICULTY_ACCENT[String(level.difficulty)]?.rgb ?? DIFFICULTY_ACCENT.hard.rgb
}

export function levelProgress(level: ChallengeLevelAccess) {
  const required = level.successful_attempts.required
  if (required <= 0) return 0
  return Math.min(100, Math.round((level.successful_attempts.count / required) * 100))
}

export function preferredChallengeLevel(levels: ChallengeLevelAccess[]) {
  return (
    levels.find((level) => level.status === 'in_progress') ??
    levels.find((level) => level.status === 'failed' || level.status === 'abandoned') ??
    levels.find((level) => level.status !== 'locked' && level.status !== 'completed') ??
    levels.find((level) => level.status === 'completed') ??
    levels[0] ??
    null
  )
}

export function actionForChallengeLevel(item: ChallengeLevelAccess): ChallengeActionIntent | null {
  if (item.status === 'locked') return null
  if (item.status === 'in_progress') return item.active_run_id ? 'resume' : null
  if (item.status === 'completed') {
    // A completed level is already counted; the only door action is an uncounted
    // free-play replay ("Replay"). Routing it through the review run avoids the
    // retry endpoint, which rejects non-primary runs - the latest run here may
    // itself be a prior replay.
    if (item.review_available) return 'review'
    return null
  }
  if (item.status === 'failed' || item.status === 'abandoned') return 'retry'
  return 'start'
}

export function actionLabel(action: ChallengeActionIntent | null, status: ChallengeLevelAccess['status']) {
  if (status === 'locked') return 'Locked'
  // 'review' is the internal mode for an uncounted free-play run; players just
  // see "Replay".
  if (action === 'review') return 'Replay'
  if (action === 'continue' || action === 'resume') return 'Continue'
  if (action === 'retry') return 'Retry'
  return 'Play'
}

export function doorStyleForLevel(level: ChallengeLevelAccess | null): CSSProperties {
  if (!level) {
    return {
      '--door-rgb': '125, 145, 175',
      '--door-glow': '144, 198, 255',
    } as CSSProperties
  }

  const accent = challengeLevelAccent(level)
  return {
    '--door-rgb': accent,
    '--door-glow': accent,
  } as CSSProperties
}
