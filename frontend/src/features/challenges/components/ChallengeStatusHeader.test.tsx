import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeRun } from '@/features/challenges/types'
import { ChallengeStatusHeader } from './ChallengeStatusHeader'

afterEach(cleanup)

const run = {
  stars: 0, status: 'failed', replay: true, challenge: { title: 'Stage a file' },
  mastery_progress: { cleared: true, stars: 3 }, completion: { stars: 3 },
  policy: { min_counted_commands: 2, max_counted_commands: 5 },
  counts: { counted_action_total: 5 },
} as ChallengeRun

describe('ChallengeStatusHeader scoring', () => {
  it('keeps a current zero-star result separate from the saved best', () => {
    render(<ChallengeStatusHeader run={run} onExit={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Star rules: 0 of 3 stars' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Star rules: 3 of 3 stars' })).not.toBeInTheDocument()
  })

  it('updates live stars from server eligibility as the target is exceeded', () => {
    const activeRun = {
      ...run, status: 'started',
      star_breakdown: { stars: 0, available_stars: 3, counted_commands: 0, command_target: 2, graded_under_previous_rules: false, retry_count: 0, criteria: [] },
    } as ChallengeRun
    const { rerender } = render(<ChallengeStatusHeader run={activeRun} />)
    expect(screen.getByText('Stars on clear')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Star rules: 3 of 3 stars available on clear' })).toBeInTheDocument()
    rerender(<ChallengeStatusHeader run={{ ...activeRun, star_breakdown: { ...activeRun.star_breakdown, available_stars: 1 } }} />)
    expect(screen.getByRole('button', { name: 'Star rules: 1 of 3 stars available on clear' })).toBeInTheDocument()
  })
})
