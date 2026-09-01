import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeRun } from '@/features/challenges/types'
import { ChallengeContextPanel } from './ChallengeContextPanel'
import { ChallengeWorkspaceTour } from './ChallengeWorkspaceTour'

const ASYNC_ASSERTION_TIMEOUT = 5_000

function addTarget(attribute: string, value?: string) {
  const element = document.createElement(attribute === 'data-command-input' ? 'input' : 'div')
  element.setAttribute(attribute, value ?? '')
  Object.defineProperty(element, 'getBoundingClientRect', {
    configurable: true,
    value: () => ({
      x: 80,
      y: 100,
      left: 80,
      top: 100,
      right: 380,
      bottom: 260,
      width: 300,
      height: 160,
      toJSON: () => ({}),
    }),
  })
  Object.defineProperty(element, 'scrollIntoView', { configurable: true, value: vi.fn() })
  document.body.appendChild(element)
}

describe('ChallengeWorkspaceTour', () => {
  afterEach(() => {
    cleanup()
    document.querySelectorAll('[data-tour-target], [data-command-input]').forEach((element) => element.remove())
    vi.restoreAllMocks()
  })

  it('keeps the Challenge order and skips unavailable optional panels', async () => {
    addTarget('data-tour-target', 'challenge-brief')
    addTarget('data-tour-target', 'star-budget')
    addTarget('data-tour-target', 'command-budget')
    addTarget('data-tour-target', 'live-dag')
    addTarget('data-command-input')
    const onClose = vi.fn()

    render(
      <ChallengeWorkspaceTour
        run={{ id: 91 } as ChallengeRun}
        onClose={onClose}
      />,
    )

    expect(
      await screen.findByRole(
        'heading',
        { name: 'Review the challenge' },
        { timeout: ASYNC_ASSERTION_TIMEOUT },
      ),
    ).toBeInTheDocument()
    expect(screen.getAllByRole('dialog', { name: 'Review the challenge' })).toHaveLength(1)
    expect(screen.getByText('Challenge quick tour')).toBeVisible()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Earn up to 3 stars' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Watch the command limit' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Track repository state' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Run a Git command' })).toBeInTheDocument()
    expect(screen.queryByText('Compare the target')).not.toBeInTheDocument()
    expect(screen.queryByText('Use the feedback')).not.toBeInTheDocument()
    expect(screen.queryByText('Check project files')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Complete the objective' })).toBeInTheDocument()
    expect(screen.getByText('6 / 6')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /start challenge/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)

  it('uses the real budget anchors and includes available project, target, and feedback panels', async () => {
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
      width: 300, height: 160, toJSON: () => ({}),
    })
    for (const target of ['live-dag', 'expected-state', 'project-files', 'feedback']) {
      addTarget('data-tour-target', target)
    }
    addTarget('data-command-input')
    const onClose = vi.fn()
    const run = {
      id: 92,
      challenge: { title: 'Save the project', narrative: 'Prepare the project.', summary: 'Commit the file.' },
      counts: { counted_action_total: 1, total_attempts: 4 },
      policy: { min_counted_commands: 2, max_counted_commands: 5 },
      mastery_progress: { stars: 0 },
    } as ChallengeRun
    const view = (currentRun: ChallengeRun) => (
      <>
        <ChallengeContextPanel run={currentRun} />
        <ChallengeWorkspaceTour run={currentRun} onClose={onClose} />
      </>
    )
    const { rerender } = render(view(run))

    expect(await screen.findByRole('heading', { name: 'Review the challenge' })).toBeInTheDocument()
    expect(screen.getByText('1 / 5')).toBeInTheDocument()
    expect(screen.getByText('≤ 2 commands')).toBeInTheDocument()
    expect(screen.queryByText('Attempts')).not.toBeInTheDocument()

    for (const heading of [
      'Earn up to 3 stars', 'Watch the command limit', 'Track repository state',
      'Compare the target', 'Check project files', 'Run a Git command',
      'Use the feedback', 'Complete the objective',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: /^next$/i }))
      expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    }
    expect(screen.getByText('9 / 9')).toBeInTheDocument()

    rerender(view({ ...run, counts: { ...run.counts, counted_action_total: 2 } }))
    expect(screen.getByText('2 / 5')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Complete the objective' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /start challenge/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)
})
