import { DifficultyActionButton } from '@/features/challenges/components/DifficultyActionButton'
import type { ChallengeLevelAccess } from '@/features/challenges/types'

export function DifficultySelector({
  difficulties,
  disabled = false,
  onStart,
  onReview,
}: {
  difficulties: ChallengeLevelAccess[]
  disabled?: boolean
  onStart: (difficulty: ChallengeLevelAccess) => void
  onReview: (difficulty: ChallengeLevelAccess) => void
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
