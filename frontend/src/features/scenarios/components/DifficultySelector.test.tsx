import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

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
  },
]

describe('DifficultySelector', () => {
  it('renders available, locked, and review states', () => {
    render(<DifficultySelector difficulties={difficulties} onStart={vi.fn()} onReview={vi.fn()} />)

    expect(screen.getByText('Not Started')).toBeInTheDocument()
    expect(screen.getByText('Locked')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /review/i })).toBeInTheDocument()
  })
})
