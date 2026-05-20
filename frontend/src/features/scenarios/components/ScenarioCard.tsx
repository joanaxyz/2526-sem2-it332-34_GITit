import { ScenarioSkillFocusCard } from '@/features/scenarios/components/ScenarioSkillFocusCard'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'

export function ScenarioCard({
  scenario,
  onStart,
  onReview,
}: {
  scenario: ScenarioSkillFocus
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <ScenarioSkillFocusCard
      scenario={scenario}
      onDifficultyAction={(_, difficulty, action) => {
        if (action === 'review') {
          onReview(difficulty)
          return
        }
        onStart(difficulty)
      }}
    />
  )
}
