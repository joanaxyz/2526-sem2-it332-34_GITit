import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import { ScenarioStatusHeader } from './ScenarioStatusHeader'

const repositoryState = {
  commits: [],
  branches: { main: null },
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const session: ScenarioSession = {
  id: 42,
  mode: 'primary',
  status: 'started',
  difficulty_instance_id: 7,
  completed_at: null,
  first_attempt_star_eligible: true,
  completion_type: 'state_based',
  scenario: {
    id: 5,
    slug: 'clean-commit',
    title: 'Commit the clean changes',
    focus: 'git commit',
    narrative: '',
  },
  module: {
    id: 3,
    number: 1,
    title: 'Basics',
  },
  difficulty: 'easy',
  variant: {
    id: 9,
    label: 'Variant A',
    changed_variant: false,
  },
  mastery_progress: {
    mastered: 0,
    required: 3,
  },
  policy: {
    id: 11,
    min_counted_commands: 3,
    max_counted_commands: 6,
    non_counted_patterns: ['git status', 'git diff'],
  },
  counts: {
    counted_action_total: 1,
    minimum_counted_commands: 3,
    maximum_counted_commands: 6,
    non_counted_diagnostic_total: 2,
    remaining_counted_commands: 5,
    max_reached: false,
    total_attempts: 3,
  },
  scaffolding: {
    live_dag: true,
    expected_state: true,
    contextual_feedback: true,
  },
  repository_state: repositoryState,
  expected_state: repositoryState,
  steps: [],
  review_mode: false,
  next_difficulty: null,
  completion: null,
}

describe('ScenarioStatusHeader', () => {
  afterEach(() => cleanup())

  it('renders a compact command budget in the header with detail text', () => {
    render(<ScenarioStatusHeader session={session} onExit={vi.fn()} />)

    expect(screen.getByRole('button', { name: /actions 1 of 6/i })).toBeInTheDocument()
    expect(screen.getByText('Target 3')).toBeInTheDocument()
    expect(screen.getAllByText('5 left').length).toBeGreaterThan(0)
    expect(screen.getByText('Counted actions used')).toBeInTheDocument()
    expect(screen.getByText('Maximum/fail limit')).toBeInTheDocument()
    expect(screen.getByText(/Diagnostic commands do not count/i)).toBeInTheDocument()
  })

  it('shows the failed state from the session status and budget state', () => {
    render(
      <ScenarioStatusHeader
        session={{
          ...session,
          status: 'failed',
          counts: {
            ...session.counts,
            counted_action_total: 6,
            remaining_counted_commands: 0,
            max_reached: true,
          },
        }}
        onExit={vi.fn()}
      />,
    )

    expect(screen.getAllByText('Failed').length).toBeGreaterThan(0)
    expect(screen.getAllByText('failed').length).toBeGreaterThan(0)
  })

  it('labels failed attempts as retry', () => {
    render(
      <ScenarioStatusHeader
        session={{ ...session, status: 'failed' }}
        onExit={vi.fn()}
        onRetry={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: /^retry$/i })).toBeInTheDocument()
  })

  it('labels active restarts as start over and calls the confirmation hook', () => {
    const onStartOver = vi.fn()
    render(<ScenarioStatusHeader session={session} onExit={vi.fn()} onStartOver={onStartOver} />)

    fireEvent.click(screen.getByRole('button', { name: /start over/i }))

    expect(onStartOver).toHaveBeenCalledTimes(1)
    expect(screen.queryByRole('button', { name: /^retry$/i })).not.toBeInTheDocument()
  })

  it('labels completed inaccurate attempts as retry for accuracy', () => {
    render(
      <ScenarioStatusHeader
        session={{
          ...session,
          status: 'completed',
          counts: { ...session.counts, counted_action_total: 4 },
        }}
        onExit={vi.fn()}
        onRetry={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: /retry for accuracy/i })).toBeInTheDocument()
  })

  it('disables Continue while a fresh mastery attempt is starting', () => {
    const onContinue = vi.fn()
    render(
      <ScenarioStatusHeader
        session={{
          ...session,
          status: 'completed',
          mastery_progress: { mastered: 1, required: 3 },
          counts: { ...session.counts, counted_action_total: 3 },
        }}
        isRetrying
        onContinue={onContinue}
        onExit={vi.fn()}
      />,
    )

    const continueButton = screen.getByRole('button', { name: /continuing/i })
    expect(continueButton).toBeDisabled()

    fireEvent.click(continueButton)

    expect(onContinue).not.toHaveBeenCalled()
  })
})
