import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { AdventureResult } from './AdventureResult'
import type { AdventureRun } from '@/features/command-adventures/types'

const run: AdventureRun = {
  id: 1,
  status: 'completed',
  command_adventure: { id: 1, slug: 'repo-basecamp', title: 'Repository Basecamp', description: '' },
  current_problem_index: 2,
  total_problems: 2,
  total_score: 90,
  mastery_progress_gained: 0.85,
  completed_at: '2026-06-07T00:00:00Z',
  current_attempt: null,
  results: [
    {
      id: 10,
      order: 0,
      status: 'completed',
      correctness_score: 100,
      efficiency_score: 100,
      independence_score: 100,
      final_score: 100,
      mastery_gain: 1,
      hint_count: 0,
      counted_command_count: 1,
    },
    {
      id: 11,
      order: 1,
      status: 'failed',
      correctness_score: 0,
      efficiency_score: 0,
      independence_score: 0,
      final_score: 40,
      mastery_gain: 0,
      hint_count: 2,
      counted_command_count: 5,
    },
  ],
  progress: { completed: 2, total: 2 },
}

describe('AdventureResult', () => {
  afterEach(() => cleanup())

  it('shows mastery percent, overall score, and per-problem bands', () => {
    render(<AdventureResult run={run} onRestart={vi.fn()} />)
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('90')).toBeInTheDocument()
    expect(screen.getByText('Mastered')).toBeInTheDocument()
    expect(screen.getByText('Failed')).toBeInTheDocument()
  })
})
