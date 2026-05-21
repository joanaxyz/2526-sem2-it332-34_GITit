import { ScenarioSkillFocusCard } from '@/features/scenarios/components/ScenarioSkillFocusCard'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'

export function ScenarioCard({
  scenario,
  topicNumber,
  onStart,
  onReview,
}: {
  scenario: ScenarioSkillFocus
  topicNumber: number
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <ScenarioSkillFocusCard
      scenario={scenario}
      topicNumber={topicNumber}
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
