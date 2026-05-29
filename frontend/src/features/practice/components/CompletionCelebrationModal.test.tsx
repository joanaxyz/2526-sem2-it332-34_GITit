import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import { CompletionCelebrationModal } from './CompletionCelebrationModal'

const repositoryState = {
  commits: [],
  branches: { main: null },
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const baseSession: ScenarioSession = {
  id: 44,
  mode: 'primary',
  status: 'failed',
  difficulty_instance_id: 12,
  completed_at: null,
  first_attempt_star_eligible: false,
  completion_type: 'state_based',
  scenario: {
    id: 9,
    slug: 'recover-from-hard-reset-incident',
    title: 'Recover from a hard reset incident',
    focus: 'hard reset recovery',
    narrative: '',
    lesson_number: 4,
    lesson_id: 12,
  },
  module: { id: 4, number: 4, title: 'Advanced Recovery History' },
  difficulty: 'easy',
  variant: { id: 3, label: 'Recover 4-1-e1', changed_variant: true },
  mastery_progress: { mastered: 0, required: 3 },
  policy: { id: 2, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
  counts: {
    counted_action_total: 6,
    minimum_counted_commands: 2,
    maximum_counted_commands: 6,
    non_counted_diagnostic_total: 1,
    remaining_counted_commands: 0,
    max_reached: true,
    total_attempts: 6,
  },
  scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true },
  repository_state: repositoryState,
  expected_state: repositoryState,
  steps: [],
  review_mode: false,
  next_difficulty: null,
  completion: null,
}

describe('CompletionCelebrationModal', () => {
  it('uses fresh-variant wording for failed sessions', () => {
    render(
      <CompletionCelebrationModal
        open
        session={baseSession}
        onClose={vi.fn()}
        onBackToModules={vi.fn()}
        onRetry={vi.fn()}
      />,
    )

    expect(screen.getByText(/start a fresh variant/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /start fresh variant/i })).toBeInTheDocument()
  })

  it('shows a lesson-review nudge when the variant has looped', () => {
    render(
      <CompletionCelebrationModal
        open
        session={{ ...baseSession, variant: { ...baseSession.variant, looped_variant: true } }}
        onClose={vi.fn()}
        onBackToModules={vi.fn()}
        onRetry={vi.fn()}
      />,
    )

    expect(screen.getByText(/cycled through all authored variants/i)).toBeInTheDocument()
  })
})
