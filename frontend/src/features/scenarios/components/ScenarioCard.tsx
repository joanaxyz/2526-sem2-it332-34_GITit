import { ScenarioSkillFocusCard } from '@/features/scenarios/components/ScenarioSkillFocusCard'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'

export function ScenarioCard({
  scenario,
  scenarioNumber,
  onStart,
  onReview,
}: {
  scenario: ScenarioSkillFocus
  scenarioNumber: number
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <ScenarioSkillFocusCard
      scenario={scenario}
      scenarioNumber={scenarioNumber}
      onDifficultyAction={(_, difficulty, action) => {
        if (action === 'review') {
          onReview(difficulty)
          return
        }
        onStart(difficulty)
      }}
      onPreview={() => {}}
    />
  )
}
