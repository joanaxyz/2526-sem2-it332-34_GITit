import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { StarTriplet } from './LevelStatValues'
import type { StarBreakdown } from './StarScoreChecklist'

afterEach(() => { cleanup(); vi.useRealTimers() })

function breakdown(counted: number, available: number): StarBreakdown {
  return {
    stars: 0,
    available_stars: available,
    counted_commands: counted,
    command_target: 1,
    generous_target: 3,
    maximum_commands: 6,
    scoring_policy_version: 2,
    retry_count: 0,
    graded_under_previous_rules: false,
    criteria: [],
  }
}

describe('live star eligibility notice', () => {
  it('explains both command thresholds as they are crossed', () => {
    const { rerender } = render(<StarTriplet runId={11} count={3} active breakdown={breakdown(1, 3)} />)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()

    rerender(<StarTriplet runId={11} count={2} active breakdown={breakdown(2, 2)} />)
    expect(screen.getByRole('status')).toHaveTextContent('3 → 2 stars available on clear')
    expect(screen.getByRole('status')).toHaveTextContent('Efficient target exceeded: 2 / 1 counted commands.')
    expect(screen.getByRole('status')).toHaveClass('gameplay-star-notice')
    expect(screen.getByRole('status').parentElement).toBe(document.body)
    expect(document.querySelectorAll('.gameplay-header-stars .is-lost')).toHaveLength(1)

    rerender(<StarTriplet runId={11} count={1} active breakdown={breakdown(4, 1)} />)
    expect(screen.getByRole('status')).toHaveTextContent('2 → 1 stars available on clear')
    expect(screen.getByRole('status')).toHaveTextContent('Generous target exceeded: 4 / 3 counted commands.')
  })

  it('does not announce free inspections or a newly loaded run', () => {
    const { rerender } = render(<StarTriplet runId={11} count={3} active breakdown={breakdown(0, 3)} />)
    rerender(<StarTriplet runId={11} count={3} active breakdown={breakdown(0, 3)} />)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    rerender(<StarTriplet runId={12} count={2} active breakdown={breakdown(2, 2)} />)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('explains a two-star drop when both targets are crossed', () => {
    const { rerender } = render(<StarTriplet runId={11} count={3} active breakdown={breakdown(1, 3)} />)
    rerender(<StarTriplet runId={11} count={1} active breakdown={breakdown(4, 1)} />)
    expect(screen.getByRole('status')).toHaveTextContent('Efficient and generous targets exceeded')
  })

  it('dismisses the notice after a short delay and clears it for a new run', () => {
    vi.useFakeTimers()
    const { rerender } = render(<StarTriplet runId={11} count={3} active breakdown={breakdown(1, 3)} />)
    rerender(<StarTriplet runId={11} count={2} active breakdown={breakdown(2, 2)} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    act(() => vi.advanceTimersByTime(4500))
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    rerender(<StarTriplet runId={11} count={1} active breakdown={breakdown(4, 1)} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    rerender(<StarTriplet runId={12} count={3} active breakdown={breakdown(0, 3)} />)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})
