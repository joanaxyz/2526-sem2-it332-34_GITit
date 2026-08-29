import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ChallengeOutcomeModal } from './ChallengeOutcomeModal'
import type { ChallengeRun } from '@/features/challenges/types'

const run = {
  id: 7,
  replay: false,
  status: 'completed',
  stars: 3,
  failure_reason: null,
  completed_at: '2026-06-30T00:00:00Z',
  challenge: {
    id: 10,
    slug: 'repo-basecamp',
    title: 'Repository Basecamp',
    summary: '',
    narrative: '',
    level_id: 101,
  },
  chapter: { id: 1, number: 1, title: 'Foundations' },
  battle_stage: null,
  difficulty: 'easy',
  variant: { id: 1, label: 'Variant A' },
  mastery_progress: { cleared: true, stars: 3 },
  policy: { min_counted_commands: 2, max_counted_commands: 5 },
  counts: {
    counted_action_total: 2,
    minimum_counted_commands: 2,
    maximum_counted_commands: 5,
    non_counted_diagnostic_total: 1,
    remaining_counted_commands: 3,
    max_reached: false,
    total_attempts: 1,
  },
  scaffolding: {
    live_dag: false,
    expected_state: false,
    contextual_feedback: false,
  },
  repository_state: {},
  visualization: { commit_dag: {} },
  expected_state: null,
  steps: [],
  next_difficulty: { id: 11, difficulty: 'medium' },
  sibling_levels: [
    { id: 101, difficulty: 'easy', status: 'completed' },
    { id: 102, difficulty: 'medium', status: 'in_progress' },
  ],
  completion: null,
} as unknown as ChallengeRun

describe('ChallengeOutcomeModal', () => {
  afterEach(() => cleanup())

  it('renders completed challenges as you won', () => {
    render(
      <ChallengeOutcomeModal
        open
        run={run}
        onClose={vi.fn()}
        onBackToMap={vi.fn()}
        onNextLevel={vi.fn()}
        onSelectLevel={vi.fn()}
        nextDifficultyLabel="Medium"
      />,
    )

    expect(screen.getByRole('dialog')).toHaveClass('game-outcome-backdrop')
    expect(screen.getByRole('img', { name: 'You Won' })).toBeInTheDocument()
    expect(screen.getByText('Level ready')).toBeInTheDocument()
    expect(screen.queryByRole('img', { name: 'Game Over' })).not.toBeInTheDocument()
  })

  it('renders failed challenges as game over', () => {
    render(
      <ChallengeOutcomeModal
        open
        run={{
          ...run,
          status: 'failed',
          stars: 0,
          counts: { ...run.counts, counted_action_total: 5, remaining_counted_commands: 0, max_reached: true },
          next_difficulty: null,
          mastery_progress: { cleared: false, stars: 0 },
        }}
        onClose={vi.fn()}
        onBackToMap={vi.fn()}
        onRetry={vi.fn()}
      />,
    )

    expect(screen.getByRole('img', { name: 'Game Over' })).toBeInTheDocument()
    expect(screen.getByText('Attempt limit reached')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /start fresh variant/i })).toBeInTheDocument()
    expect(screen.queryByRole('img', { name: 'You Won' })).not.toBeInTheDocument()
  })
})
