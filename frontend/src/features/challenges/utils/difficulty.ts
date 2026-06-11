import type { ChallengeQuestAccess } from '@/features/challenges/types'

export function nextDifficultyInSequence<T extends { difficulty: string }>(
  difficulties: readonly T[],
  currentDifficulty: string,
) {
  const currentIndex = difficulties.findIndex((difficulty) => difficulty.difficulty === currentDifficulty)
  return currentIndex >= 0 ? difficulties[currentIndex + 1] ?? null : null
}

export function nextAvailableDifficultyAfter(
  difficulties: readonly ChallengeQuestAccess[],
  currentDifficulty: string,
) {
  const nextDifficulty = nextDifficultyInSequence(difficulties, currentDifficulty)
  return nextDifficulty && nextDifficulty.status !== 'locked' ? nextDifficulty : null
}
