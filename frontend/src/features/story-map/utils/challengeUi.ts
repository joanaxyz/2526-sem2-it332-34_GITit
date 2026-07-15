import type {
  ChallengeActionIntent,
  ChallengeSummary,
  ChallengeTrialAccess,
  AdventureSummary,
} from '@/features/challenges/types'

// Per-difficulty label + accent (RGB triplet consumed via `rgba(var(--), )`).
export const DIFFICULTY_ACCENT: Record<string, { label: string; rgb: string }> = {
  easy: { label: 'Easy', rgb: 'var(--theme-primary-rgb)' },
  medium: { label: 'Medium', rgb: 'var(--theme-rail-rgb)' },
  hard: { label: 'Hard', rgb: 'var(--theme-challenge-rgb)' },
}

export function adventureActionLabel(adventure: AdventureSummary) {
  if (adventure.status === 'completed') return 'Replay'
  if (adventure.latest_run_id) return 'Replay'
  return 'Play'
}

export function challengeTrials(challenge: ChallengeSummary): ChallengeTrialAccess[] {
  return challenge.trials
}

export function allChallengeTrials(challenges: ChallengeSummary[]): ChallengeTrialAccess[] {
  return challenges.flatMap((challenge) => challengeTrials(challenge))
}

export function difficultyLabel(level: ChallengeTrialAccess) {
  return DIFFICULTY_ACCENT[String(level.difficulty)]?.label ?? String(level.difficulty)
}

export function challengeLevelAccent(level: ChallengeTrialAccess | null) {
  if (!level) return DIFFICULTY_ACCENT.hard.rgb
  return DIFFICULTY_ACCENT[String(level.difficulty)]?.rgb ?? DIFFICULTY_ACCENT.hard.rgb
}

export function preferredChallengeLevel(levels: ChallengeTrialAccess[]) {
  return (
    levels.find((level) => level.status === 'in_progress') ??
    levels.find((level) => level.status === 'failed' || level.status === 'abandoned') ??
    levels.find((level) => level.status !== 'locked' && level.status !== 'completed') ??
    levels.find((level) => level.status === 'completed') ??
    levels[0] ??
    null
  )
}

export function actionForChallengeLevel(item: ChallengeTrialAccess): ChallengeActionIntent | null {
  if (item.status === 'locked') return null
  if (item.status === 'in_progress') return 'start'
  if (item.status === 'completed') {
    if (item.replay_available) return 'replay'
    return null
  }
  if (item.status === 'failed' || item.status === 'abandoned') return 'retry'
  return 'start'
}

export function actionLabel(action: ChallengeActionIntent | null, status: ChallengeTrialAccess['status']) {
  if (status === 'locked') return 'Locked'
  if (action === 'replay') return 'Replay'
  if (action === 'retry') return 'Retry'
  return 'Play'
}
