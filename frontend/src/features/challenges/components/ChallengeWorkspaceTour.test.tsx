import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeRun } from '@/features/challenges/types'
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
    expect(await screen.findByRole('heading', { name: 'Track repository state' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'Run a Git command' })).toBeInTheDocument()
    expect(screen.getByText('3 / 3')).toBeInTheDocument()
    expect(screen.queryByText('Compare the target')).not.toBeInTheDocument()
    expect(screen.queryByText('Use the feedback')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /start challenge/i }))
    expect(onClose).toHaveBeenCalledOnce()
  }, 15_000)
})
