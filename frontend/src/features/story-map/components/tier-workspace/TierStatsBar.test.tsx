import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

import { TierStatsBar } from './TierStatsBar'

function makeRun(overrides: Partial<TierRun> = {}): TierRun {
  return {
    replay: false,
    difficulty: 'easy',
    stars: 2,
    policy: { min_counted_commands: 1, max_counted_commands: 12 },
    counts: { counted_action_total: 3 },
    ...overrides,
  } as unknown as TierRun
}

function statValue(label: string) {
  const term = screen.getByText(label, { selector: 'dt' })
  return term.nextElementSibling as HTMLElement
}

afterEach(cleanup)

describe('TierStatsBar', () => {
  it('shows mode, difficulty, stars, command budget and star target', () => {
    render(<TierStatsBar run={makeRun()} />)

    expect(statValue('Mode')).toHaveTextContent('Adventure')
    expect(statValue('Difficulty')).toHaveTextContent('Easy')
    expect(within(statValue('Stars')).getByLabelText('2 of 3 stars')).toBeInTheDocument()
    expect(statValue('Commands')).toHaveTextContent('3 / 12')
    expect(statValue('Star target')).toHaveTextContent('≤ 1 command')
  })

  it('carries the tour anchors for the command budget and star target', () => {
    render(<TierStatsBar run={makeRun()} />)

    expect(document.querySelector('[data-tour-target="command-budget"]')).toHaveTextContent('3 / 12')
    expect(document.querySelector('[data-tour-target="star-budget"]')).toHaveTextContent('≤ 1 command')
  })

  it('pluralizes the star target, marks replays and omits a missing difficulty', () => {
    render(
      <TierStatsBar
        run={makeRun({
          replay: true,
          difficulty: null as unknown as TierRun['difficulty'],
          policy: { min_counted_commands: 3, max_counted_commands: 8 },
        })}
      />,
    )

    expect(statValue('Mode')).toHaveTextContent('Adventure · Replay')
    expect(screen.queryByText('Difficulty')).not.toBeInTheDocument()
    expect(statValue('Star target')).toHaveTextContent('≤ 3 commands')
  })
})
