import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { ModuleCard } from './ModuleCard'
import type { LearningModule } from '@/features/modules/types'

vi.mock('@/features/modules/components/ModuleScenarioHub', () => ({
  ModuleScenarioHub: () => <div>Scenario Skill Focus cards</div>,
}))

const practiceModule: LearningModule = {
  id: 2,
  slug: 'local-repository-foundations',
  number: 1,
  title: 'Local Repository Foundations',
  description: 'Practice local Git workflows.',
  is_orientation: false,
  sort_order: 1,
  lesson_count: 0,
  scenario_count: 2,
  practice_completion: { value: 0, numerator: 0, denominator: 2 },
  lessons: [
    {
      id: 21,
      slug: 'internal-anchor',
      title: 'Internal Anchor',
      subtitle: 'Not a student-facing page.',
      sort_order: 1,
      is_complete: false,
      scenario_count: 0,
    },
  ],
}

describe('ModuleCard', () => {
  it('shows Scenario Skill Focus cards directly for practice modules without overview links', () => {
    render(
      <MemoryRouter>
        <ModuleCard
          module={practiceModule}
          isExpanded
          scenarioSummary={[]}
          onToggle={vi.fn()}
        />
      </MemoryRouter>,
    )

    expect(screen.getByText('Scenario Skill Focus cards')).toBeInTheDocument()
    expect(screen.queryByText(/overviews/i)).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /view overview/i })).not.toBeInTheDocument()
    expect(screen.queryByText('Internal Anchor')).not.toBeInTheDocument()
  })
})
