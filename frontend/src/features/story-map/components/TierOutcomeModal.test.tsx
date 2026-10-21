import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ComponentProps } from 'react'

import type { GameOutcomeModal } from '@/shared/level/components/game-outcome/GameOutcomeModal'
import type { TierRun } from './tierWorkspaceTypes'
import { TierOutcomeModal } from './TierOutcomeModal'

const shown = vi.hoisted(() => vi.fn())
vi.mock('@/shared/audio/battleAudio', () => ({ playGameOverSound: vi.fn(), playVictorySound: vi.fn() }))
vi.mock('@/shared/level/components/game-outcome/GameOutcomeModal', () => ({
  GameOutcomeModal: (props: ComponentProps<typeof GameOutcomeModal>) => {
    shown(props)
    return <div><h1>{props.headline}</h1><p>{props.message}</p>{props.actions}</div>
  },
}))

afterEach(() => { cleanup(); shown.mockClear() })

describe('transfer checkpoint outcomes', () => {
  it.each(['failed', 'completed'] as const)('preserves the first %s result and offers ungraded practice', (status) => {
    const run = {
      transfer: true, replay: false, status, stars: 0, difficulty: 'hard',
      tier: { id: 7, difficulty: 'easy', adventure_level_id: 3, adventure_level_slug: 'staging-and-committing', adventure_level_title: 'Staging and Committing', adventure_level_number: 3 },
      progress: { completed: status === 'completed' ? 1 : 0, total: 1, cleared: status === 'completed', next_scenario: null },
      scenario: { index: 1, total: 1, title: '' },
      reward: { coins: 50, claimed: true },
      counts: { counted_action_total: 4, minimum_counted_commands: 3, maximum_counted_commands: 4,
        non_counted_diagnostic_total: 1, total_attempts: 5, max_reached: true },
    } as TierRun
    const practice = vi.fn()
    render(<TierOutcomeModal open run={run} onClose={() => {}} onBackToMap={() => {}} onRetry={practice} />)
    expect(screen.getByText(/later runs cannot change this checkpoint result/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Try again' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Continue free practice' }))
    expect(practice).toHaveBeenCalledOnce()
    expect(shown.mock.calls.at(-1)?.[0]).toMatchObject({ showStars: false, stars: undefined, title: 'Transfer result recorded' })
  })
})

describe('ordered scenario outcomes', () => {
  const clearedScenario = (overrides: Partial<TierRun> = {}) =>
    ({
      transfer: false, replay: false, status: 'completed', stars: 3, difficulty: 'easy',
      tier: { id: 7, difficulty: 'easy', adventure_level_id: 3, adventure_level_slug: 'staging-and-committing', adventure_level_title: 'Staging and Committing', adventure_level_number: 3 },
      next_difficulty: null,
      progress: {
        completed: 1, total: 2, cleared: false,
        next_scenario: { index: 2, slug: 'publish-and-track', title: 'Publish and track' },
      },
      scenario: { index: 1, total: 2, title: 'Publish a branch' },
      reward: { coins: 25, claimed: false },
      counts: { counted_action_total: 2, minimum_counted_commands: 2, maximum_counted_commands: 12,
        non_counted_diagnostic_total: 0, total_attempts: 2, max_reached: false },
      ...overrides,
    }) as TierRun

  it.each([
    { status: 'completed', replay: false },
    { status: 'failed', replay: false },
    { status: 'completed', replay: true },
    { status: 'failed', replay: true },
  ] as const)('names the level for a $status result (replay: $replay)', ({ status, replay }) => {
    render(<TierOutcomeModal open run={clearedScenario({ status, replay })} onClose={() => {}} onBackToMap={() => {}} />)
    expect(shown.mock.calls.at(-1)?.[0]).toMatchObject({ level: { label: 'Level 3', title: 'Staging and Committing' } })
  })

  it('names the scenario just cleared, the next scenario and the reward it unlocks', () => {
    render(<TierOutcomeModal open run={clearedScenario()} onClose={() => {}} onBackToMap={() => {}} />)
    expect(screen.getByText('Scenario cleared')).toBeInTheDocument()
    expect(
      screen.getByText('Scenario 1 of 2 cleared — next: Publish and track. Clear it to earn 25 GitCoins.'),
    ).toBeInTheDocument()
    // A partial clear does not claim the tier is complete.
    const props = shown.mock.calls.at(-1)?.[0]
    expect(props).toMatchObject({ title: 'Scenario complete' })
    render(<>{props?.badges}</>)
    expect(screen.getByText('Easy scenario 1 of 2')).toBeInTheDocument()
    expect(screen.queryByText('Easy complete')).not.toBeInTheDocument()
  })

  it('keeps Continue after the final difficulty and returns to the map', () => {
    const backToMap = vi.fn()
    const run = clearedScenario({ difficulty: 'hard', progress: { completed: 2, total: 2, cleared: true, next_scenario: null } })
    render(<TierOutcomeModal open run={run} onClose={() => {}} onBackToMap={backToMap} />)

    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(backToMap).toHaveBeenCalledOnce()
  })
})
