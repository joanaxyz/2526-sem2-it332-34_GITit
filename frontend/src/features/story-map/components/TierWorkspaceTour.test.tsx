import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { TierWorkspaceTour } from './TierWorkspaceTour'

const ASYNC_ASSERTION_TIMEOUT = 5_000

function addTarget(attribute: string, value?: string) {
  const element = document.createElement(attribute === 'data-command-input' ? 'input' : 'div')
  element.setAttribute(attribute, value ?? '')
  Object.defineProperty(element, 'getBoundingClientRect', {
    configurable: true,
    value: () => ({
      x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
      width: 300, height: 160, toJSON: () => ({}),
    }),
  })
  Object.defineProperty(element, 'scrollIntoView', { configurable: true, value: vi.fn() })
  document.body.appendChild(element)
}

// The anchors here are the ones the tier-workspace panels (TierStatsBar, TierObjectivesCard...) render, so
// a renamed target fails this test instead of silently killing the whole tour:
// GameplayWorkspaceTour renders nothing when a required step cannot resolve.
function addRequiredTierTargets() {
  for (const target of ['tier-brief', 'tier-story', 'star-budget', 'command-budget', 'live-dag', 'project-files']) {
    addTarget('data-tour-target', target)
  }
  addTarget('data-testid', 'battle-stage')
  addTarget('data-command-input')
}

describe('TierWorkspaceTour', () => {
  afterEach(() => {
    cleanup()
    document
      .querySelectorAll('[data-tour-target], [data-command-input], [data-testid="battle-stage"]')
      .forEach((element) => element.remove())
    vi.restoreAllMocks()
  })

  it('walks the tier workspace and skips panels this tier does not show', async () => {
    addRequiredTierTargets()
    const onClose = vi.fn()

    render(<TierWorkspaceTour runId={41} onClose={onClose} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    expect(screen.getByText('Level quick tour')).toBeVisible()

    for (const heading of [
      'Reread the story', 'Earn up to 3 stars', 'Watch the command limit', 'See command results',
      'Track repository state', 'Check project files', 'Run a Git command',
      'Complete the objective',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.queryByText('Compare the target')).not.toBeInTheDocument()
    expect(screen.queryByText('Use the feedback')).not.toBeInTheDocument()
    expect(screen.getByText('9 / 9')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /start level/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)

  it('includes the target diagram and feedback panel when the tier renders them', async () => {
    addRequiredTierTargets()
    addTarget('data-tour-target', 'expected-state')
    addTarget('data-tour-target', 'feedback')

    render(<TierWorkspaceTour runId={42} onClose={vi.fn()} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    for (const heading of [
      'Reread the story', 'Earn up to 3 stars', 'Watch the command limit', 'See command results',
      'Track repository state', 'Compare the target', 'Check project files',
      'Run a Git command', 'Use the feedback', 'Complete the objective',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.getByText('11 / 11')).toBeInTheDocument()
  }, 15_000)

  async function openLiveDagStep(targetInDrawer?: boolean) {
    addRequiredTierTargets()
    render(<TierWorkspaceTour runId={43} onClose={vi.fn()} targetInDrawer={targetInDrawer} />)
    await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT })
    for (const heading of [
      'Reread the story', 'Earn up to 3 stars', 'Watch the command limit', 'See command results',
      'Track repository state',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      await screen.findByRole('heading', { name: heading })
    }
  }

  it('mentions the target graph on the live step when the target sits in the drawer', async () => {
    await openLiveDagStep(true)

    expect(screen.getByText(/and the target graph to compare it with/)).toBeInTheDocument()
  }, 15_000)

  it('keeps the plain live step text when there is no target in a drawer', async () => {
    await openLiveDagStep()

    expect(
      screen.getByText('The live diagram shows the current commits, branches, and HEAD after every valid command.'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/target graph/)).not.toBeInTheDocument()
  }, 15_000)
})
