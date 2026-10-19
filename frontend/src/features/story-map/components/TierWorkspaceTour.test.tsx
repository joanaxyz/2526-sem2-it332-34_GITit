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

  it('covers the objective, scoring, command limit and terminal in four steps', async () => {
    addRequiredTierTargets()
    const onClose = vi.fn()

    render(<TierWorkspaceTour runId={41} onClose={onClose} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    expect(screen.getByText('Level quick tour')).toBeVisible()

    for (const heading of ['Earn up to 3 stars', 'Watch the command limit', 'Run a Git command']) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
      if (heading === 'Earn up to 3 stars') {
        expect(screen.getByText('Finish within the Star target with no more than one retry.')).toBeInTheDocument()
        expect(screen.getByText('Finish within the Star target after two or more retries.')).toBeInTheDocument()
      }
    }
    expect(screen.queryByText('Compare the target')).not.toBeInTheDocument()
    expect(screen.queryByText('Use the feedback')).not.toBeInTheDocument()
    expect(screen.getByText('4 / 4')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /start level/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)

  it('stays at four steps even when optional panels are available', async () => {
    addRequiredTierTargets()
    addTarget('data-tour-target', 'expected-state')
    addTarget('data-tour-target', 'feedback')

    render(<TierWorkspaceTour runId={42} onClose={vi.fn()} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    for (const heading of ['Earn up to 3 stars', 'Watch the command limit', 'Run a Git command']) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.getByText('4 / 4')).toBeInTheDocument()
  }, 15_000)

  async function openCommandStep(targetInDrawer?: boolean) {
    addRequiredTierTargets()
    render(<TierWorkspaceTour runId={43} onClose={vi.fn()} targetInDrawer={targetInDrawer} />)
    await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT })
    for (const heading of ['Earn up to 3 stars', 'Watch the command limit', 'Run a Git command']) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      await screen.findByRole('heading', { name: heading })
    }
  }

  it('mentions the target graph on the command step when the target sits in the drawer', async () => {
    await openCommandStep(true)

    expect(screen.getByText(/compare it with the target graph/)).toBeInTheDocument()
  }, 15_000)

  it('keeps the plain command step text when there is no target in a drawer', async () => {
    await openCommandStep()

    expect(
      screen.getByText(/Use project files and the repository diagrams to check your work/),
    ).toBeInTheDocument()
    expect(screen.queryByText(/target graph/)).not.toBeInTheDocument()
  }, 15_000)
})
