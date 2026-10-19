import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { FloatingGuideMascot } from './FloatingGuideMascot'

const originalWidth = window.innerWidth
const originalHeight = window.innerHeight
beforeEach(() => { localStorage.clear() })
afterEach(() => {
  cleanup()
  Object.defineProperty(window, 'innerWidth', { configurable: true, value: originalWidth })
  Object.defineProperty(window, 'innerHeight', { configurable: true, value: originalHeight })
  vi.restoreAllMocks()
})

function drag(button: HTMLElement) {
  fireEvent.pointerDown(button, { button: 0, pointerId: 1, clientX: 100, clientY: 100 })
  fireEvent.pointerMove(button, { pointerId: 1, clientX: 20, clientY: 180 })
  fireEvent.pointerUp(button, { pointerId: 1, clientX: 20, clientY: 180 })
  fireEvent.click(button)
}

describe('floating command guide mascot', () => {
  it('opens on click and lives outside the workspace header', () => {
    const onActivate = vi.fn()
    const view = render(<header><FloatingGuideMascot label="Open command guide" onActivate={onActivate} /></header>)
    expect(view.container.querySelector('button')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Open command guide' }))
    expect(onActivate).toHaveBeenCalledOnce()
  })

  it('moves without opening, then opens on the next normal click', () => {
    const onActivate = vi.fn()
    render(<FloatingGuideMascot label="Open command guide" onActivate={onActivate} />)
    const button = screen.getByRole('button', { name: 'Open command guide' })
    const launcher = button.parentElement!
    const before = launcher.getAttribute('style')
    drag(button)
    expect(launcher.getAttribute('style')).not.toBe(before)
    expect(onActivate).not.toHaveBeenCalled()
    fireEvent.click(button)
    expect(onActivate).toHaveBeenCalledOnce()
  })

  it('keeps its position across mounts and stays within a resized viewport', () => {
    const view = render(<FloatingGuideMascot label="Open command guide" onActivate={vi.fn()} />)
    fireEvent.keyDown(screen.getByRole('button'), { key: 'ArrowLeft', shiftKey: true })
    const before = screen.getByRole('button').parentElement!.getAttribute('style')
    view.unmount()
    render(<FloatingGuideMascot label="Open command guide" onActivate={vi.fn()} />)
    expect(screen.getByRole('button').parentElement!.getAttribute('style')).toBe(before)
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 240 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 220 })
    act(() => window.dispatchEvent(new Event('resize')))
    const position = screen.getByRole('button').parentElement!.style
    expect(parseFloat(position.left) + 76).toBeLessThanOrEqual(240)
    expect(parseFloat(position.top) + 104).toBeLessThanOrEqual(220)
  })

  it('hides while its guide is open and returns to the same position when closed', () => {
    const onActivate = vi.fn()
    const view = render(<FloatingGuideMascot label="Open command guide" onActivate={onActivate} />)
    const button = screen.getByRole('button')
    drag(button)
    const launcher = button.parentElement!
    const position = launcher.getAttribute('style')

    view.rerender(<FloatingGuideMascot label="Command guide is open" active onActivate={onActivate} />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(launcher).toHaveAttribute('aria-hidden', 'true')
    expect(launcher).toHaveAttribute('inert')
    expect(button).toBeInTheDocument()

    view.rerender(<FloatingGuideMascot label="Open command guide" onActivate={onActivate} />)
    expect(screen.getByRole('button')).toBe(button)
    expect(launcher).not.toHaveAttribute('inert')
    expect(launcher).not.toHaveAttribute('aria-hidden')
    expect(launcher.getAttribute('style')).toBe(position)
    expect(onActivate).not.toHaveBeenCalled()
  })
})
