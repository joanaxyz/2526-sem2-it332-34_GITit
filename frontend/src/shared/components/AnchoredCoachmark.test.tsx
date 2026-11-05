import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { AnchoredCoachmark } from './AnchoredCoachmark'

let frames: Map<number, FrameRequestCallback>
let target: HTMLButtonElement
let targetRect: DOMRect

function nextFrame() {
  const pending = [...frames.values()]
  frames.clear()
  act(() => pending.forEach((callback) => callback(performance.now())))
}

function setup(onDismiss = vi.fn()) {
  return render(<AnchoredCoachmark targetSelector="#moving-guide" title="Meet Git-It"
    body="Click the map to move your guide." step={{ current: 1, total: 2 }} onDismiss={onDismiss} />)
}

beforeEach(() => {
  frames = new Map()
  let frameId = 0
  vi.stubGlobal('innerWidth', 1024)
  vi.stubGlobal('innerHeight', 768)
  vi.stubGlobal('visualViewport', undefined)
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    frames.set(++frameId, callback)
    return frameId
  })
  vi.stubGlobal('cancelAnimationFrame', (id: number) => frames.delete(id))
  vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockImplementation(() => Math.min(304, window.innerWidth - 32))
  vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(200)
  targetRect = new DOMRect(40, 200, 64, 80)
  target = document.createElement('button')
  target.id = 'moving-guide'
  target.getBoundingClientRect = () => targetRect
  document.body.append(target)
})

afterEach(() => {
  cleanup()
  target.remove()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('AnchoredCoachmark', () => {
  it('follows a moving target without a scroll or resize event and flips toward the screen center', () => {
    setup()
    const popup = screen.getByRole('status')
    expect(popup.style.left).toBe('120px')
    expect(popup.dataset.caret).toBe('left')

    targetRect = new DOMRect(700, 400, 64, 80)
    nextFrame()
    expect(popup.style.left).toBe('380px')
    expect(popup.style.top).toBe('340px')
    expect(popup.dataset.caret).toBe('right')
  })

  it.each([[4, 4], [250, 4], [4, 480], [250, 480]])('keeps the popup on a narrow screen at target position %s, %s', (x, y) => {
    vi.stubGlobal('innerWidth', 320)
    vi.stubGlobal('innerHeight', 568)
    targetRect = new DOMRect(x, y, 64, 80)
    setup()
    const popup = screen.getByRole('status')
    const left = Number.parseFloat(popup.style.left)
    const top = Number.parseFloat(popup.style.top)
    expect(left).toBeGreaterThanOrEqual(16)
    expect(left + popup.offsetWidth).toBeLessThanOrEqual(304)
    expect(top).toBeGreaterThanOrEqual(16)
    expect(top + popup.offsetHeight).toBeLessThanOrEqual(552)
  })

  it('tracks target transforms and launcher-parent movement before the next animation frame', async () => {
    const launcher = document.createElement('div')
    document.body.append(launcher)
    launcher.append(target)
    setup()
    const popup = screen.getByRole('status')
    await act(async () => {
      targetRect = new DOMRect(300, 200, 64, 80)
      target.style.transform = 'translateX(260px)'
    })
    expect(popup.style.left).toBe('380px')
    await act(async () => {
      targetRect = new DOMRect(700, 400, 64, 80)
      launcher.style.left = '700px'
    })
    expect(popup.dataset.caret).toBe('right')
    expect(popup.style.top).toBe('340px')
    expect(frames.size).toBe(1)
    launcher.remove()
  })

  it('hides with a hidden or missing launcher and returns when the target is visible', () => {
    setup()
    const popup = screen.getByRole('status')
    target.setAttribute('aria-hidden', 'true')
    nextFrame()
    expect(popup).not.toBeVisible()
    expect(popup).toHaveAttribute('aria-hidden', 'true')
    target.removeAttribute('aria-hidden')
    nextFrame()
    expect(popup).toBeVisible()
    target.remove()
    nextFrame()
    expect(popup).not.toBeVisible()
    document.body.append(target)
    nextFrame()
    expect(popup).toBeVisible()
  })

  it('accounts for the smaller visual viewport when the keyboard is open', () => {
    vi.stubGlobal('visualViewport', { offsetLeft: 0, offsetTop: 200, width: 390, height: 300 })
    targetRect = new DOMRect(280, 240, 64, 80)
    setup()
    const popup = screen.getByRole('status')
    expect(Number.parseFloat(popup.style.top)).toBeGreaterThanOrEqual(216)
    expect(Number.parseFloat(popup.style.top) + popup.offsetHeight).toBeLessThanOrEqual(484)
  })

  it('provides keyboard dismissal and cancels its tracking frame on unmount', () => {
    const dismiss = vi.fn()
    const { unmount } = setup(dismiss)
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss Meet Git-It introduction' }))
    fireEvent.keyDown(screen.getByRole('button', { name: 'Got it' }), { key: 'Escape' })
    expect(dismiss).toHaveBeenCalledTimes(2)
    expect(frames.size).toBe(1)
    unmount()
    expect(frames.size).toBe(0)
  })
})
