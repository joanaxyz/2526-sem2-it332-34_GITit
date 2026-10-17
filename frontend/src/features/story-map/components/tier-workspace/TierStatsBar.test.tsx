import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { createRef } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

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

  it('has no Repo graph button unless the layout uses the drawer', () => {
    render(<TierStatsBar run={makeRun()} />)

    expect(screen.queryByRole('button', { name: /repo graph/i })).not.toBeInTheDocument()
  })

  it('opens the drawer from the Repo graph button and flags unseen graph changes', () => {
    const onOpen = vi.fn()
    const trigger = { open: false, hasUpdate: true, controls: 'tier-repo-graph', buttonRef: createRef<HTMLButtonElement>(), onOpen }
    const { rerender } = render(<TierStatsBar run={makeRun()} repoGraph={trigger} />)

    const button = screen.getByRole('button', { name: 'Repo graph, updated' })
    expect(button).toHaveAttribute('aria-haspopup', 'dialog')
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(button).toHaveAttribute('aria-controls', 'tier-repo-graph')
    expect(button.querySelector('.tier-repo-graph-dot')).not.toBeNull()
    expect(trigger.buttonRef.current).toBe(button)

    fireEvent.click(button)
    expect(onOpen).toHaveBeenCalledOnce()

    rerender(<TierStatsBar run={makeRun()} repoGraph={{ ...trigger, open: true, hasUpdate: false }} />)
    expect(screen.getByRole('button', { name: 'Repo graph' })).toHaveAttribute('aria-expanded', 'true')
    expect(document.querySelector('.tier-repo-graph-dot')).toBeNull()
  })
})
