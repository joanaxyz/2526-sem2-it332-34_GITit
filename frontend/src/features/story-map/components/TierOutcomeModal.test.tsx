import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ComponentProps } from 'react'

import type { GameOutcomeModal } from '@/shared/level/components/game-outcome/GameOutcomeModal'
import type { TierRun } from './tierWorkspaceTypes'
import { TierOutcomeModal } from './TierOutcomeModal'
import { tierOutcomeNextStep } from './tierOutcome'

const shown = vi.hoisted(() => vi.fn())
vi.mock('@/shared/audio/battleAudio', () => ({ playGameOverSound: vi.fn(), playVictorySound: vi.fn() }))
vi.mock('@/shared/level/components/game-outcome/GameOutcomeModal', () => ({
  GameOutcomeModal: (props: ComponentProps<typeof GameOutcomeModal>) => {
    shown(props)
    return <div><h1>{props.headline}</h1><p>{props.message}</p></div>
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
    const step = tierOutcomeNextStep({ run, onBackToMap: () => {}, onRetry: practice })
    expect(step).toMatchObject({ caption: 'Practice', prompt: 'Click me to keep practicing!' })
    step?.onSelect()
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
      screen.getByText('Next: Publish and track'),
    ).toBeInTheDocument()
    // A partial clear does not claim the tier is complete.
    const props = shown.mock.calls.at(-1)?.[0]
    expect(props).toMatchObject({ title: 'Scenario complete' })
    expect(props?.badges).toBeNull()
    render(<>{props?.progress}</>)
    expect(screen.getByRole('heading', { name: 'Easy scenarios' })).toBeInTheDocument()
    expect(screen.queryByText('Easy scenario 1 of 2')).not.toBeInTheDocument()
    expect(screen.queryByText('Easy complete')).not.toBeInTheDocument()
  })

  it('offers the next scenario through the mascot after a partial clear', () => {
    const continueTier = vi.fn()
    const step = tierOutcomeNextStep({ run: clearedScenario(), onBackToMap: vi.fn(), onContinue: continueTier })

    expect(step).toMatchObject({
      prompt: 'Click me to continue to the next scenario!',
      detail: 'Next: Publish and track',
    })
    step?.onSelect()
    expect(continueTier).toHaveBeenCalledOnce()
  })

  it('offers the next difficulty once the tier is cleared', () => {
    const nextLevel = vi.fn()
    const run = clearedScenario({
      next_difficulty: { id: 8, difficulty: 'medium' } as TierRun['next_difficulty'],
      progress: { completed: 2, total: 2, cleared: true, next_scenario: null },
    })
    const step = tierOutcomeNextStep({ run, onBackToMap: vi.fn(), onNextLevel: nextLevel })

    expect(step?.prompt).toBe('Click me to continue to the Medium tier!')
    step?.onSelect()
    expect(nextLevel).toHaveBeenCalledOnce()

    render(<TierOutcomeModal open run={run} onClose={vi.fn()} onBackToMap={vi.fn()} onNextDifficulty={nextLevel} onRetry={vi.fn()} />)
    render(<>{shown.mock.calls.at(-1)?.[0].footerActions}</>)
    fireEvent.click(screen.getByRole('button', { name: 'Continue to Medium' }))
    expect(nextLevel).toHaveBeenCalledTimes(2)
    expect(screen.getByRole('button', { name: 'Play again' })).toBeInTheDocument()
  })

  it('offers a retry after a failed run', () => {
    const retry = vi.fn()
    const step = tierOutcomeNextStep({ run: clearedScenario({ status: 'failed' }), onBackToMap: vi.fn(), onRetry: retry })

    expect(step?.prompt).toBe('Click me to try again!')
    step?.onSelect()
    expect(retry).toHaveBeenCalledOnce()
  })

  it.each([
    { difficulty: 'easy', completed: 1, total: 2, cleared: false, expected: '1 of 2 cleared · 1 more to unlock Medium' },
    { difficulty: 'easy', completed: 2, total: 2, cleared: true, expected: '2 of 2 cleared · Medium unlocked' },
    { difficulty: 'medium', completed: 1, total: 3, cleared: false, expected: '1 of 3 cleared · 2 more to unlock Hard' },
    { difficulty: 'medium', completed: 3, total: 3, cleared: true, expected: '3 of 3 cleared · Hard unlocked' },
    { difficulty: 'hard', completed: 1, total: 2, cleared: false, expected: '1 of 2 cleared · 1 more to finish Hard' },
    { difficulty: 'hard', completed: 2, total: 2, cleared: true, expected: '2 of 2 cleared · Hard tier complete' },
  ] as const)('shows the current $difficulty scenario stepper', ({ difficulty, completed, total, cleared, expected }) => {
    const run = clearedScenario({
      difficulty,
      progress: { completed, total, cleared, next_scenario: cleared ? null : { index: completed + 1, slug: 'next', title: 'Next' } },
    })
    render(<TierOutcomeModal open run={run} onClose={vi.fn()} onBackToMap={vi.fn()} />)
    render(<>{shown.mock.calls.at(-1)?.[0].progress}</>)
    expect(screen.getByText(expected)).toBeInTheDocument()
    const stepper = screen.getByRole('region', { name: `${difficulty[0].toUpperCase()}${difficulty.slice(1)} scenario progress` })
    expect(stepper).toContainElement(screen.getByRole('heading', { name: `${difficulty[0].toUpperCase()}${difficulty.slice(1)} scenarios` }))
    expect(stepper.querySelectorAll('.is-cleared')).toHaveLength(completed)
    expect(stepper.querySelectorAll('li')).toHaveLength(total)
  })

  it.each([
    { difficulty: 'easy', suffix: 'unlock Medium' },
    { difficulty: 'medium', suffix: 'unlock Hard' },
    { difficulty: 'hard', suffix: 'finish Hard' },
  ] as const)('keeps saved $difficulty progress visible after a failure or replay', ({ difficulty, suffix }) => {
    const progress = { completed: 1, total: 2, cleared: false, next_scenario: null }
    for (const overrides of [{ status: 'failed' }, { replay: true }] as const) {
      const run = clearedScenario({ ...overrides, difficulty, progress })
      render(<TierOutcomeModal open run={run} onClose={vi.fn()} onBackToMap={vi.fn()} />)
      render(<>{shown.mock.calls.at(-1)?.[0].progress}</>)
      expect(screen.getByText(`1 of 2 cleared · 1 more to ${suffix}`)).toBeInTheDocument()
      expect(screen.getByRole('listitem', { name: 'Scenario 1 cleared' })).toBeInTheDocument()
      expect(screen.getByRole('listitem', { name: 'Scenario 2 remaining' })).toBeInTheDocument()
      cleanup()
    }
  })

  it('returns to the map after the final difficulty', () => {
    const backToMap = vi.fn()
    const run = clearedScenario({ difficulty: 'hard', progress: { completed: 2, total: 2, cleared: true, next_scenario: null } })
    const step = tierOutcomeNextStep({ run, onBackToMap: backToMap, onRetry: vi.fn() })

    expect(step?.prompt).toBe('Click me to head back to the map!')
    step?.onSelect()
    expect(backToMap).toHaveBeenCalledOnce()
  })

  it('offers nothing while the run is still in progress', () => {
    expect(tierOutcomeNextStep({ run: clearedScenario({ status: 'started' }), onBackToMap: vi.fn() })).toBeNull()
  })
})

describe('a ready transfer checkpoint', () => {
  const clearedHardTier = {
    transfer: false, replay: false, status: 'completed', stars: 3, difficulty: 'hard',
    transfer_checkpoint: { tier_id: 7, title: 'Resolving Conflicts Manually', run_id: null },
    next_difficulty: null,
    tier: { id: 7, difficulty: 'hard', adventure_level_id: 3, adventure_level_slug: 'resolving-conflicts-manually', adventure_level_title: 'Resolving Conflicts Manually', adventure_level_number: 1 },
    progress: { completed: 2, total: 2, cleared: true, next_scenario: null },
    scenario: { index: 2, total: 2, title: '' },
    reward: { coins: 50, claimed: true },
    counts: { counted_action_total: 3, minimum_counted_commands: 3, maximum_counted_commands: 8,
      non_counted_diagnostic_total: 0, total_attempts: 3, max_reached: false },
  } as unknown as TierRun

  it('is offered on the cleared screen and by the mascot', () => {
    const take = vi.fn()
    render(<TierOutcomeModal open run={clearedHardTier} onClose={() => {}} onBackToMap={() => {}} onTransfer={take} />)
    expect(screen.getByText(/A transfer checkpoint is ready/)).toBeInTheDocument()
    render(<>{shown.mock.calls.at(-1)?.[0].footerActions}</>)
    fireEvent.click(screen.getByRole('button', { name: 'Take transfer checkpoint' }))
    expect(take).toHaveBeenCalledOnce()
    const step = tierOutcomeNextStep({ run: clearedHardTier, onBackToMap: () => {}, onTransfer: take })
    expect(step).toMatchObject({ caption: 'Transfer checkpoint', detail: 'Resolving Conflicts Manually' })
  })

  it('tells a practice run that the recorded result has not changed', () => {
    const run = { ...clearedHardTier, transfer: true, replay: true, transfer_checkpoint: null } as TierRun
    render(<TierOutcomeModal open run={run} onClose={() => {}} onBackToMap={() => {}} />)
    expect(screen.getByText(/recorded transfer result has not changed/)).toBeInTheDocument()
    expect(shown.mock.calls.at(-1)?.[0]).toMatchObject({ showStars: false, title: 'Practice complete' })
  })

  it('is absent when no checkpoint waits', () => {
    const run = { ...clearedHardTier, transfer_checkpoint: null } as TierRun
    render(<TierOutcomeModal open run={run} onClose={() => {}} onBackToMap={() => {}} onTransfer={() => {}} />)
    expect(screen.queryByText(/A transfer checkpoint is ready/)).not.toBeInTheDocument()
    expect(tierOutcomeNextStep({ run, onBackToMap: () => {} })).toMatchObject({ caption: 'Map' })
  })
})
