import type { CSSProperties } from 'react'

import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  CommandAdventureSummary,
} from '@/features/challenges/types'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/shared/practice/utils/commandAccuracy'

// Per-difficulty label + accent (RGB triplet consumed via `rgba(var(--…), …)`).
export const DIFFICULTY_ACCENT: Record<string, { label: string; rgb: string }> = {
  easy: { label: 'Easy', rgb: '0, 245, 212' },
  medium: { label: 'Medium', rgb: '53, 143, 255' },
  hard: { label: 'Hard', rgb: '176, 74, 255' },
}

export const REWARD_MARKERS = [
  { value: 25, label: '+25 XP' },
  { value: 50, label: '+60 XP' },
  { value: 75, label: '+100 XP' },
  { value: 100, label: 'Crown chest' },
]

export function nextReward(progress: number) {
  return REWARD_MARKERS.find((marker) => progress < marker.value) ?? REWARD_MARKERS[REWARD_MARKERS.length - 1]
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
    const progressComplete = item.successful_attempts.count >= item.successful_attempts.required
    const latestAccuracy = item.latest_attempt?.accuracy_rate ?? null
    if (item.review_available && progressComplete && meetsMasteryAccuracy(latestAccuracy)) return 'review'
    if (meetsProgressAccuracy(latestAccuracy)) return 'continue'
    return 'retry'
  }
  if (item.status === 'failed' || item.status === 'abandoned') return 'retry'
  return 'start'
}

export function actionLabel(action: ChallengeActionIntent | null, status: ChallengeLevelAccess['status']) {
  if (status === 'locked') return 'Locked'
  if (action === 'review') return 'Review'
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
