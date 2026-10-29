import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { WorkspaceTour } from './WorkspaceTour'

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

// The anchors here are the ones the workspace panels (WorkspaceStatsBar, ObjectivesCard...) render, so
// a renamed target fails this test instead of silently killing the whole tour:
// GameplayWorkspaceTour renders nothing when a required step cannot resolve.
function addRequiredTierTargets() {
  for (const target of ['tier-brief', 'tier-story', 'star-budget', 'command-budget', 'live-dag', 'project-files']) {
    addTarget('data-tour-target', target)
  }
  addTarget('data-testid', 'battle-stage')
  addTarget('data-command-input')
}

describe('WorkspaceTour', () => {
  afterEach(() => {
    cleanup()
    document
      .querySelectorAll('[data-tour-target], [data-command-input], [data-testid="battle-stage"]')
      .forEach((element) => element.remove())
    vi.restoreAllMocks()
  })

  it('introduces the objective, scoring, diagrams, files, and terminal in six steps', async () => {
    addRequiredTierTargets()
    const onClose = vi.fn()

    render(<WorkspaceTour runId={41} onClose={onClose} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    expect(screen.getByText('Level quick tour')).toBeVisible()

    for (const heading of [
      'Earn up to 3 stars',
      'Watch the command limit',
      'Read the repository diagrams',
      'Browse project files',
      'Run a Git command',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
      if (heading === 'Earn up to 3 stars') {
        expect(screen.getByText('Finish within the efficient command target.')).toBeInTheDocument()
        expect(screen.getByText('Finish above the efficient target but within the generous target.')).toBeInTheDocument()
      }
    }
    expect(screen.queryByText('Compare the target')).not.toBeInTheDocument()
    expect(screen.queryByText('Use the feedback')).not.toBeInTheDocument()
    expect(screen.getByText('6 / 6')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /start level/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)

  it('keeps the tour focused when optional panels are available', async () => {
    addRequiredTierTargets()
    addTarget('data-tour-target', 'expected-state')
    addTarget('data-tour-target', 'feedback')

    render(<WorkspaceTour runId={42} onClose={vi.fn()} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    for (const heading of [
      'Earn up to 3 stars',
      'Watch the command limit',
      'Read the repository diagrams',
      'Browse project files',
      'Run a Git command',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.getByText('6 / 6')).toBeInTheDocument()
  }, 15_000)

async function openCommandStep(repoGraphInDrawer?: boolean) {
    addRequiredTierTargets()
  render(<WorkspaceTour runId={43} onClose={vi.fn()} repoGraphInDrawer={repoGraphInDrawer} />)
    await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT })
    for (const heading of [
      'Earn up to 3 stars',
      'Watch the command limit',
      'Read the repository diagrams',
      'Browse project files',
      'Run a Git command',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      await screen.findByRole('heading', { name: heading })
    }
  }

  it('speaks for a Challenge Gate trial in challenge mode', async () => {
    addRequiredTierTargets()
    const onClose = vi.fn()

    render(<WorkspaceTour mode="challenge" runId={44} onClose={onClose} />)

    expect(
      await screen.findByRole('heading', { name: 'Review the objective' }, { timeout: ASYNC_ASSERTION_TIMEOUT }),
    ).toBeInTheDocument()
    expect(screen.getByText('Challenge quick tour')).toBeVisible()
    for (let step = 0; step < 5; step += 1) fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
    fireEvent.click(await screen.findByRole('button', { name: /start challenge/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)

  it('introduces the live diagram from the Repo graph button in drawer mode', async () => {
    await openCommandStep(true)

    fireEvent.click(screen.getByRole('button', { name: /^back$/i }))
    expect(screen.getByRole('heading', { name: 'Browse project files' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /^back$/i }))
    expect(screen.getByRole('heading', { name: 'Read the repository diagrams' })).toBeInTheDocument()
    expect(screen.getByText(/Open Repo graph to see the live commits/)).toBeInTheDocument()
    expect(screen.getByText(/compare its repository shape/)).toBeInTheDocument()
  }, 15_000)

  it('uses the visible diagram target when the graph is not in a drawer', async () => {
    await openCommandStep()

    fireEvent.click(screen.getByRole('button', { name: /^back$/i }))
    fireEvent.click(screen.getByRole('button', { name: /^back$/i }))
    expect(screen.getByRole('heading', { name: 'Read the repository diagrams' })).toBeInTheDocument()
    expect(screen.getByText(/If a target diagram is shown/)).toBeInTheDocument()
  }, 15_000)
})
