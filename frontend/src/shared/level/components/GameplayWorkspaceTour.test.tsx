import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { CircleHelp } from 'lucide-react'
import { useState } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  GameplayWorkspaceTour,
  type WorkspaceTourStep,
} from './GameplayWorkspaceTour'

const originalWidth = window.innerWidth
const originalHeight = window.innerHeight
const ASYNC_ASSERTION_TIMEOUT = 5_000

function rect({
  left = 80,
  top = 100,
  width = 240,
  height = 120,
}: Partial<DOMRect> = {}) {
  return {
    x: left,
    y: top,
    left,
    top,
    width,
    height,
    right: left + width,
    bottom: top + height,
    toJSON: () => ({}),
  } as DOMRect
}

function addTarget(
  id: string,
  currentRect: () => DOMRect = () => rect(),
  tagName: 'div' | 'input' = 'div',
) {
  const element = document.createElement(tagName)
  element.dataset.testTourTarget = id
  Object.defineProperty(element, 'getBoundingClientRect', {
    configurable: true,
    value: currentRect,
  })
  Object.defineProperty(element, 'scrollIntoView', {
    configurable: true,
    value: vi.fn(),
  })
  document.body.appendChild(element)
  return element
}

function step(id: string, optional = false): WorkspaceTourStep {
  return {
    id,
    selector: `[data-test-tour-target="${id}"]`,
    icon: CircleHelp,
    title: `${id} title`,
    body: `${id} guidance`,
    placement: 'bottom',
    optional,
  }
}

function FocusRestorationHarness({ onClose }: { onClose: (reason: string) => void }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>Open tour</button>
      {open ? (
        <GameplayWorkspaceTour
          label="Gameplay guide"
          steps={[step('first')]}
          onClose={(reason) => {
            onClose(reason)
            setOpen(false)
          }}
        />
      ) : null}
    </>
  )
}

describe('GameplayWorkspaceTour', () => {
  afterEach(() => {
    cleanup()
    document.querySelectorAll('[data-test-tour-target]').forEach((element) => element.remove())
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: originalWidth })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: originalHeight })
    vi.restoreAllMocks()
  })

  it('shows one step at a time and supports Back, Next, and Finish', async () => {
    addTarget('first')
    addTarget('second', () => rect({ left: 540, top: 160 }))
    const onClose = vi.fn()

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first'), step('second')]}
        onClose={onClose}
      />,
    )

    expect(
      await screen.findByRole(
        'heading',
        { name: 'first title' },
        { timeout: ASYNC_ASSERTION_TIMEOUT },
      ),
    ).toBeInTheDocument()
    expect(screen.getByText('Gameplay guide')).toBeVisible()
    expect(screen.queryByText('second guidance')).not.toBeInTheDocument()
    expect(screen.getAllByRole('dialog', { name: 'first title' })).toHaveLength(1)

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(await screen.findByRole('heading', { name: 'second title' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /back/i }))
    expect(await screen.findByRole('heading', { name: 'first title' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))
    fireEvent.click(await screen.findByRole('button', { name: /start playing/i }))
    expect(onClose).toHaveBeenCalledWith('finish')
  }, 15_000)

  it('skips missing optional targets and keeps progress accurate', async () => {
    addTarget('first')
    addTarget('last', () => rect({ left: 520, top: 120 }))

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first'), step('optional', true), step('last')]}
        onClose={vi.fn()}
      />,
    )

    expect(await screen.findByText('1 / 2')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /next/i }))

    expect(await screen.findByRole('heading', { name: 'last title' })).toBeInTheDocument()
    expect(screen.getByText('2 / 2')).toBeInTheDocument()
    expect(screen.queryByText('optional guidance')).not.toBeInTheDocument()
  })

  it('waits for a missing required target instead of permanently skipping it', async () => {
    addTarget('first')
    const onClose = vi.fn()

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first'), step('required')]}
        onClose={onClose}
      />,
    )

    await act(async () => {
      await new Promise((resolve) => window.requestAnimationFrame(resolve))
    })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).not.toHaveBeenCalled()

    addTarget('required', () => rect({ left: 520, top: 120 }))

    expect(await screen.findByRole('heading', { name: 'first title' })).toBeInTheDocument()
    expect(screen.getByText('1 / 2')).toBeInTheDocument()
  })

  it('uses accessible progress controls to jump across the filtered step list', async () => {
    addTarget('first')
    addTarget('last', () => rect({ left: 520, top: 120 }))

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first'), step('optional', true), step('last')]}
        onClose={vi.fn()}
      />,
    )

    const firstProgress = await screen.findByRole('button', {
      name: 'Go to step 1: first title',
    })
    const lastProgress = screen.getByRole('button', {
      name: 'Go to step 2: last title',
    })
    expect(firstProgress).toHaveAttribute('aria-current', 'step')

    fireEvent.click(lastProgress)

    expect(await screen.findByRole('heading', { name: 'last title' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Go to step 2: last title' }),
    ).toHaveAttribute('aria-current', 'step')
    expect(
      screen.getByRole('button', { name: 'Go to step 1: first title' }),
    ).not.toHaveAttribute('aria-current')
  })

  it('preserves plain input caret arrows and uses Alt+Arrow or Escape for the tour', async () => {
    const input = addTarget('command', () => rect({ left: 90, top: 180, width: 300, height: 40 }), 'input')
    addTarget('feedback', () => rect({ left: 480, top: 180 }))
    const onClose = vi.fn()

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('command'), step('feedback')]}
        onClose={onClose}
      />,
    )

    expect(await screen.findByRole('heading', { name: 'command title' })).toBeInTheDocument()
    input.focus()
    fireEvent.keyDown(input, { key: 'ArrowRight' })
    expect(screen.getByRole('heading', { name: 'command title' })).toBeInTheDocument()

    const firstStepBoundary = new KeyboardEvent('keydown', {
      key: 'ArrowLeft',
      altKey: true,
      bubbles: true,
      cancelable: true,
    })
    input.dispatchEvent(firstStepBoundary)
    expect(firstStepBoundary.defaultPrevented).toBe(true)
    expect(screen.getByRole('heading', { name: 'command title' })).toBeInTheDocument()

    fireEvent.keyDown(input, { altKey: true, key: 'ArrowRight' })
    expect(await screen.findByRole('heading', { name: 'feedback title' })).toBeInTheDocument()

    const lastStepBoundary = new KeyboardEvent('keydown', {
      key: 'ArrowRight',
      altKey: true,
      bubbles: true,
      cancelable: true,
    })
    window.dispatchEvent(lastStepBoundary)
    expect(lastStepBoundary.defaultPrevented).toBe(true)
    expect(screen.getByRole('heading', { name: 'feedback title' })).toBeInTheDocument()

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledWith('skip')
  })

  it('reattaches measurement when a target element is replaced', async () => {
    const initialTarget = addTarget('first', () => rect({ top: 100 }))

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first')]}
        onClose={vi.fn()}
      />,
    )

    expect(await screen.findByTestId('workspace-tour-spotlight')).toHaveStyle({ top: '91px' })

    const replacement = addTarget('first', () => rect({ top: 320 }))
    initialTarget.replaceWith(replacement)

    await waitFor(() => {
      expect(screen.getByTestId('workspace-tour-spotlight')).toHaveStyle({ top: '311px' })
    })
  })

  it('remeasures placement using the mounted card height', async () => {
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 800 })
    addTarget('first', () => rect({ top: 600, height: 80 }))
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (
      this: HTMLElement,
    ) {
      if (this.classList.contains('workspace-tour__card')) {
        return rect({ width: 352, height: 320 })
      }
      return rect()
    })

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('first')]}
        onClose={vi.fn()}
      />,
    )

    const dialog = await screen.findByRole('dialog', { name: 'first title' })
    await waitFor(() => expect(dialog).toHaveStyle({ top: '262px' }))
  })

  it('scrolls an offscreen narrow target before measuring its card', async () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 390 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 844 })
    let scrolled = false
    const target = addTarget('mobile', () =>
      scrolled
        ? rect({ left: 12, top: 92, width: 366, height: 250 })
        : rect({ left: 12, top: 980, width: 366, height: 250 }),
    )
    const scrollIntoView = vi.fn(() => {
      scrolled = true
    })
    Object.defineProperty(target, 'scrollIntoView', { configurable: true, value: scrollIntoView })

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        steps={[step('mobile')]}
        onClose={vi.fn()}
      />,
    )

    await waitFor(() => expect(scrollIntoView).toHaveBeenCalled())
    await act(async () => {
      await new Promise((resolve) => window.setTimeout(resolve, 260))
    })
    expect(await screen.findByRole('dialog', { name: 'mobile title' })).toBeInTheDocument()
    expect(screen.getByTestId('workspace-tour-spotlight')).toHaveStyle({ top: '83px' })
  })

  it('prioritizes a long final action over the optional keyboard hint', async () => {
    addTarget('first')

    render(
      <GameplayWorkspaceTour
        label="Gameplay guide"
        finishLabel="Choose my character"
        steps={[step('first')]}
        onClose={vi.fn()}
      />,
    )

    const finish = await screen.findByRole('button', { name: 'Choose my character' })
    expect(finish.parentElement).toHaveClass('is-compact')
  })

  it('treats Skip as dismissal and restores focus to the launch control', async () => {
    addTarget('first')
    const onClose = vi.fn()

    render(<FocusRestorationHarness onClose={onClose} />)
    const launcher = screen.getByRole('button', { name: 'Open tour' })
    launcher.focus()
    fireEvent.click(launcher)

    const dialog = await screen.findByRole('dialog', { name: 'first title' })
    await waitFor(() => expect(dialog).toHaveFocus())
    fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }))

    expect(onClose).toHaveBeenCalledWith('skip')
    await waitFor(() => expect(launcher).toHaveFocus())
  })
})
