import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ScenarioSkillFocusCard } from './ScenarioSkillFocusCard'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'

const scenario: ScenarioSkillFocus = {
  id: 1,
  slug: 'initialize-project-and-first-commit',
  title: 'Initialize and save the first snapshot',
  focus: 'git init',
  summary: 'Turn a folder into a repository.',
  skill_focus_type: 'workflow_specific',
  primary_focus_commands: ['git init'],
  learning_unit_id: 1,
  lesson_id: 1,
  difficulties: [
    {
      id: 10,
      difficulty: 'easy',
      status: 'not_started',
      review_available: false,
      mastery_progress: { mastered: 0, required: 3 },
      active_session_id: null,
      retry_session_id: null,
      policy: { id: 1, min_counted_commands: 3, max_counted_commands: 5 },
      completion: null,
      latest_attempt: null,
    },
  ],
}

describe('ScenarioSkillFocusCard', () => {
  afterEach(() => cleanup())

  it('labels scenario skill focuses as lessons without the legacy label', () => {
    render(
      <ScenarioSkillFocusCard
        scenario={scenario}
        scenarioNumber={2}
        onDifficultyAction={vi.fn()}
        onPreview={vi.fn()}
      />,
    )

    expect(screen.getByText('Lesson 2')).toBeInTheDocument()
    expect(screen.getByLabelText(/expand lesson 2/i)).toBeInTheDocument()
    expect(screen.queryByText(new RegExp('top' + 'ic', 'i'))).not.toBeInTheDocument()
  })
})
