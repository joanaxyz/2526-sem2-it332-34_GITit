import { DifficultyActionButton } from '@/features/challenges/components/DifficultyActionButton'
import type { ChallengeQuestAccess } from '@/features/challenges/types'

export function DifficultySelector({
  difficulties,
  disabled = false,
  onStart,
  onReview,
}: {
  difficulties: ChallengeQuestAccess[]
  disabled?: boolean
  onStart: (difficulty: ChallengeQuestAccess) => void
  onReview: (difficulty: ChallengeQuestAccess) => void
}) {
  return (
    <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
      {difficulties.map((difficulty) => (
        <DifficultyActionButton
          disabled={disabled}
          difficulty={difficulty}
          key={difficulty.id}
          onAction={(selectedDifficulty, action) => {
            if (action === 'review') {
              onReview(selectedDifficulty)
              return
            }
            onStart(selectedDifficulty)
          }}
        />
      ))}
    </div>
  )
}
