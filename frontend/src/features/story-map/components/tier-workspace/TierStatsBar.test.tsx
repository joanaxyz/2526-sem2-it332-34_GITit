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
    policy: { min_counted_commands: 1, max_counted_commands: 12, generous_counted_commands: 7 },
    counts: { counted_action_total: 3 },
    reward: { coins: 35, claimed: false },
    scenario: { index: 1, total: 1, title: '' },
    ...overrides,
  } as unknown as TierRun
}

function statValue(label: string) {
  const term = screen.getByText(label, { selector: 'dt' })
  return term.nextElementSibling as HTMLElement
}

afterEach(cleanup)

describe('TierStatsBar', () => {
  it('shows essential run stats without command-target indicators', () => {
    render(<TierStatsBar run={makeRun()} />)

    expect(statValue('Mode')).toHaveTextContent('Adventure')
    expect(statValue('Difficulty')).toHaveTextContent('Easy')
    expect(within(statValue('Stars')).getByLabelText('2 of 3 stars')).toBeInTheDocument()
    expect(statValue('Commands')).toHaveTextContent('3 / 12')
    expect(screen.queryByText('Star target')).not.toBeInTheDocument()
    expect(screen.queryByText('2-star target')).not.toBeInTheDocument()
  })

  it('shows the tier reward before play and marks it claimed once paid', () => {
    const { unmount } = render(<TierStatsBar run={makeRun()} />)
    expect(statValue('Reward')).toHaveTextContent('+35 GitCoins')
    unmount()

    render(<TierStatsBar run={makeRun({ reward: { coins: 35, claimed: true } })} />)
    expect(statValue('Reward')).toHaveTextContent('Claimed')
  })

  it('shows the scenario position only for a tier with several scenarios', () => {
    const { unmount } = render(<TierStatsBar run={makeRun()} />)
    expect(screen.queryByText('Scenario', { selector: 'dt' })).not.toBeInTheDocument()
    unmount()

    render(<TierStatsBar run={makeRun({ scenario: { index: 2, total: 3, title: 'Publish and track' } })} />)
    expect(statValue('Scenario')).toHaveTextContent('2 / 3')
  })

  it('counts a reward paid by this run as claimed', () => {
    render(
      <TierStatsBar
        run={makeRun({
          rewards: {
            first_level_clear: false,
            coins_awarded: 35,
            chapter_chests_awarded: [],
            mastery_advanced: [],
          },
        })}
      />,
    )
    expect(statValue('Reward')).toHaveTextContent('Claimed')
  })

  it('carries the tour anchors for the command budget and star target', () => {
    render(<TierStatsBar run={makeRun()} />)

    expect(document.querySelector('[data-tour-target="command-budget"]')).toHaveTextContent('3 / 12')
    expect(document.querySelector('[data-tour-target="star-budget"]')).toContainElement(screen.getByLabelText('2 of 3 stars'))
  })

  it('marks replays and omits a missing difficulty', () => {
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
    expect(screen.queryByText('Star target')).not.toBeInTheDocument()
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
