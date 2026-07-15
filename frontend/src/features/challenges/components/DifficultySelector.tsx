import { DifficultyActionButton } from '@/features/challenges/components/DifficultyActionButton'
import type { ChallengeTrialAccess } from '@/features/challenges/types'

export function DifficultySelector({
  difficulties,
  disabled = false,
  onStart,
  onReplay,
}: {
  difficulties: ChallengeTrialAccess[]
  disabled?: boolean
  onStart: (difficulty: ChallengeTrialAccess) => void
  onReplay: (difficulty: ChallengeTrialAccess) => void
}) {
  return (
    <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
      {difficulties.map((difficulty) => (
        <DifficultyActionButton
          disabled={disabled}
          difficulty={difficulty}
          key={difficulty.id}
          onAction={(selectedDifficulty, action) => {
            if (action === 'replay') {
              onReplay(selectedDifficulty)
              return
            }
            onStart(selectedDifficulty)
          }}
        />
      ))}
    </div>
  )
}
