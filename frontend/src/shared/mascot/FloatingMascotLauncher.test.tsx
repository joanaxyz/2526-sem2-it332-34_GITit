import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { setGuideMascotVisibility } from './guideMascotVisibility'
import { FloatingMascotLauncher } from './FloatingMascotLauncher'

const originalWidth = window.innerWidth
const originalHeight = window.innerHeight
beforeEach(() => { localStorage.clear() })
afterEach(() => {
  cleanup()
  Object.defineProperty(window, 'innerWidth', { configurable: true, value: originalWidth })
  Object.defineProperty(window, 'innerHeight', { configurable: true, value: originalHeight })
  setGuideMascotVisibility(true)
  vi.restoreAllMocks()
})

function launcher(props: { open?: boolean; onOpen?: () => void } = {}) {
  return <FloatingMascotLauncher name="test" label="Open command guide" caption="Guide" onOpen={vi.fn()} {...props} />
}

function drag(button: HTMLElement) {
  fireEvent.pointerDown(button, { button: 0, pointerId: 1, clientX: 100, clientY: 100 })
  fireEvent.pointerMove(button, { pointerId: 1, clientX: 20, clientY: 180 })
  fireEvent.pointerUp(button, { pointerId: 1, clientX: 20, clientY: 180 })
  fireEvent.click(button)
}

describe('floating mascot launcher', () => {
  it('shows Git-It and opens on click, outside the page it floats over', () => {
    const onOpen = vi.fn()
    const view = render(<header>{launcher({ onOpen })}</header>)
    expect(view.container.querySelector('button')).toBeNull()
    const button = screen.getByRole('button', { name: 'Open command guide' })
    expect(button.querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
    expect(button).toHaveTextContent('Guide')
    fireEvent.click(button)
    expect(onOpen).toHaveBeenCalledOnce()
  })

  it('keeps Git-It when the roaming mascot is hidden', () => {
    setGuideMascotVisibility(false)
    render(launcher())
    expect(screen.getByRole('button', { name: 'Open command guide' }).querySelector('img')).toHaveAttribute('src', '/mascot/portrait.png')
  })

  it('moves without opening, then opens on the next normal click', () => {
    const onOpen = vi.fn()
    render(launcher({ onOpen }))
    const button = screen.getByRole('button', { name: 'Open command guide' })
    const frame = button.parentElement!
    const before = frame.getAttribute('style')
    drag(button)
    expect(frame.getAttribute('style')).not.toBe(before)
    expect(onOpen).not.toHaveBeenCalled()
    fireEvent.click(button)
    expect(onOpen).toHaveBeenCalledOnce()
  })

  it('keeps its position across mounts and stays within a resized viewport', () => {
    const view = render(launcher())
    fireEvent.keyDown(screen.getByRole('button'), { key: 'ArrowLeft', shiftKey: true })
    const before = screen.getByRole('button').parentElement!.getAttribute('style')
    view.unmount()
    render(launcher())
    expect(screen.getByRole('button').parentElement!.getAttribute('style')).toBe(before)
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 240 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 220 })
    act(() => window.dispatchEvent(new Event('resize')))
    const position = screen.getByRole('button').parentElement!.style
    expect(parseFloat(position.left) + 76).toBeLessThanOrEqual(240)
    expect(parseFloat(position.top) + 104).toBeLessThanOrEqual(220)
  })

  it('hides while what it opens is showing and returns to the same position after', () => {
    const onOpen = vi.fn()
    const view = render(launcher({ onOpen }))
    const button = screen.getByRole('button')
    drag(button)
    const frame = button.parentElement!
    const position = frame.getAttribute('style')

    view.rerender(launcher({ onOpen, open: true }))
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(frame).toHaveAttribute('aria-hidden', 'true')
    expect(frame).toHaveAttribute('inert')
    expect(button).toBeInTheDocument()

    view.rerender(launcher({ onOpen }))
    expect(screen.getByRole('button')).toBe(button)
    expect(frame).not.toHaveAttribute('inert')
    expect(frame).not.toHaveAttribute('aria-hidden')
    expect(frame.getAttribute('style')).toBe(position)
    expect(onOpen).not.toHaveBeenCalled()
  })
})
