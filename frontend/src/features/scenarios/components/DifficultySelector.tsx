import { DifficultyActionButton } from '@/features/scenarios/components/DifficultyActionButton'
import type { WorkflowLevelAccess } from '@/features/scenarios/types'

export function DifficultySelector({
  difficulties,
  disabled = false,
  onStart,
  onReview,
}: {
  difficulties: WorkflowLevelAccess[]
  disabled?: boolean
  onStart: (difficulty: WorkflowLevelAccess) => void
  onReview: (difficulty: WorkflowLevelAccess) => void
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
