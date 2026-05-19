import { DifficultyActionButton } from '@/features/scenarios/components/DifficultyActionButton'
import type { DifficultyAccess } from '@/features/scenarios/types'

export function DifficultySelector({
  difficulties,
  onStart,
  onReview,
}: {
  difficulties: DifficultyAccess[]
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
      {difficulties.map((difficulty) => (
        <DifficultyActionButton
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
