import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DifficultySelector } from './DifficultySelector'
import type { DifficultyAccess } from '@/features/scenarios/types'

const difficulties: DifficultyAccess[] = [
  {
    id: 1,
    difficulty: 'easy',
    status: 'not_started',
    review_available: false,
    active_session_id: null,
    retry_session_id: null,
    policy: { id: 1, min_counted_commands: 3, max_counted_commands: 9, non_counted_patterns: [] },
    completion: null,
    latest_attempt: null,
  },
  {
    id: 2,
    difficulty: 'medium',
    status: 'locked',
    review_available: false,
    active_session_id: null,
    retry_session_id: null,
    policy: { id: 2, min_counted_commands: 2, max_counted_commands: 9, non_counted_patterns: [] },
    completion: null,
    latest_attempt: null,
  },
  {
    id: 3,
    difficulty: 'hard',
    status: 'completed',
    review_available: true,
    active_session_id: null,
    retry_session_id: null,
    policy: { id: 3, min_counted_commands: 1, max_counted_commands: 9, non_counted_patterns: [] },
    completion: { first_attempt_star: true, counted_action_total: 1, completed_at: '2026-05-18T00:00:00Z' },
    latest_attempt: {
      id: 3,
      status: 'completed',
      accuracy_rate: 100,
      command_accurate: true,
      counted_action_total: 1,
      total_attempts: 1,
      completed_at: '2026-05-18T00:00:00Z',
      ended_at: '2026-05-18T00:00:00Z',
    },
  },
]

describe('DifficultySelector', () => {
  afterEach(() => cleanup())

  it('renders available, locked, and review states', () => {
    render(<DifficultySelector difficulties={difficulties} onStart={vi.fn()} onReview={vi.fn()} />)

    const startButtons = screen.getAllByRole('button', { name: /start/i })
    expect(startButtons[0]).not.toBeDisabled()
    expect(startButtons[1]).toBeDisabled()
    expect(screen.getByRole('button', { name: /review/i })).toBeInTheDocument()
    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.queryByText(/counted action/i)).not.toBeInTheDocument()
  })

  it('renders retry for an active session instead of continuing the same variant', () => {
    render(
      <DifficultySelector
        difficulties={[
          {
            ...difficulties[0],
            status: 'in_progress',
            active_session_id: 99,
            latest_attempt: {
              id: 99,
              status: 'started',
              accuracy_rate: null,
              command_accurate: null,
              counted_action_total: 1,
              total_attempts: 1,
              completed_at: null,
              ended_at: null,
            },
          },
        ]}
        onStart={vi.fn()}
        onReview={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /continue/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /in progress/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /start/i })).not.toBeInTheDocument()
  })

  it('keeps completed scenarios retryable until accuracy reaches 100%', () => {
    render(
      <DifficultySelector
        difficulties={[
          {
            ...difficulties[2],
            review_available: false,
            retry_session_id: 7,
            latest_attempt: {
              ...difficulties[2].latest_attempt!,
              id: 7,
              accuracy_rate: 67,
              command_accurate: false,
              counted_action_total: 3,
            },
          },
        ]}
        onStart={vi.fn()}
        onReview={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /review/i })).not.toBeInTheDocument()
    expect(screen.getByText('67%')).toBeInTheDocument()
  })
})
