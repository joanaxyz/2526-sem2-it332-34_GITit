import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MascotSprite, type MascotPose } from './MascotSprite'

vi.mock('@/shared/sprites/preload', () => ({
  warmImages: vi.fn().mockResolvedValue(undefined),
  warmImage: vi.fn().mockResolvedValue(undefined),
  getWarmedImage: (src: string) => ({ src }),
}))

const drawImage = vi.fn()

let now = 0
let reduced = false
let hidden = false
let motionChanges: EventTarget
let frames: Map<number, FrameRequestCallback>

beforeEach(() => {
  vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
  now = 0
  reduced = hidden = false
  motionChanges = new EventTarget()
  frames = new Map()
  drawImage.mockClear()
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
    clearRect: vi.fn(), drawImage, imageSmoothingEnabled: false,
  } as unknown as CanvasRenderingContext2D)
  let id = 0
  vi.spyOn(Math, 'random').mockReturnValue(0.5)
  vi.spyOn(performance, 'now').mockImplementation(() => now)
  vi.spyOn(document, 'hidden', 'get').mockImplementation(() => hidden)
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    frames.set(++id, callback)
    return id
  })
  vi.stubGlobal('cancelAnimationFrame', (frame: number) => frames.delete(frame))
  vi.stubGlobal('matchMedia', () => ({
    get matches() { return reduced },
    addEventListener: motionChanges.addEventListener.bind(motionChanges),
    removeEventListener: motionChanges.removeEventListener.bind(motionChanges),
  }))
})
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

function sheet() { return screen.getByRole('img').firstElementChild as HTMLCanvasElement }
function paintedSource() { return (drawImage.mock.lastCall?.[0] as HTMLImageElement | undefined)?.src ?? '' }
function paintedPosition() { return drawImage.mock.lastCall?.slice(1, 3) }
function wait(milliseconds: number) { act(() => vi.advanceTimersByTime(milliseconds)) }
function animate(milliseconds: number) {
  act(() => {
    for (let elapsed = 0; elapsed < milliseconds; elapsed += 20) {
      now += 20
      const pending = [...frames.values()]
      frames.clear()
      pending.forEach((callback) => callback(now))
    }
  })
}
function motion(value: boolean) {
  act(() => { reduced = value; motionChanges.dispatchEvent(new Event('change')) })
}
function visibility(value: boolean) {
  act(() => { hidden = value; document.dispatchEvent(new Event('visibilitychange')) })
}

describe('mascot ground-idle actions', () => {
  it('keeps regular idle by default for drills and other surfaces', () => {
    render(<MascotSprite pose="idle" />)
    wait(60000)
    expect(paintedSource()).toContain('/mascot/idle.png')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('waits a random interval, plays all 64 frames once, and returns to idle before scheduling again', () => {
    render(<MascotSprite pose="idle" idleActions />)
    wait(12999)
    expect(paintedSource()).toContain('/mascot/idle.png')
    wait(1)
    expect(paintedSource()).toContain('/mascot/random.png')
    expect(sheet().width).toBe(256)
    expect(sheet().height).toBe(256)
    expect(screen.getByRole('img').style.width).toBe('160px')
    animate(2640)
    expect(paintedSource()).toContain('/mascot/random.png')
    expect(paintedPosition()).toEqual([1792, 1792])
    animate(100)
    expect(paintedSource()).toContain('/mascot/idle.png')
    wait(12999)
    expect(paintedSource()).toContain('/mascot/idle.png')
    wait(1)
    expect(paintedSource()).toContain('/mascot/random.png')
  })

  it.each<MascotPose>(['float', 'fly', 'take-off', 'land', 'walk', 'run', 'die'])(
    'does not schedule idle actions during %s', (pose) => {
      render(<MascotSprite pose={pose} idleActions />)
      wait(60000)
      expect(paintedSource()).toContain(`/mascot/${pose}.png`)
      expect(vi.getTimerCount()).toBe(0)
    },
  )

  it('cancels pending and playing actions when movement starts and waits afresh on the next idle', () => {
    const view = render(<MascotSprite pose="idle" idleActions />)
    wait(6000)
    view.rerender(<MascotSprite pose="walk" idleActions />)
    wait(20000)
    expect(paintedSource()).toContain('/mascot/walk.png')
    view.rerender(<MascotSprite pose="idle" idleActions />)
    wait(13000)
    expect(paintedSource()).toContain('/mascot/random.png')
    view.rerender(<MascotSprite pose="take-off" idleActions />)
    animate(3000)
    wait(20000)
    expect(paintedSource()).toContain('/mascot/take-off.png')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('stops an action when the Home opt-in is removed', () => {
    const view = render(<MascotSprite pose="idle" idleActions />)
    wait(13000)
    expect(paintedSource()).toContain('/mascot/random.png')
    view.rerender(<MascotSprite pose="idle" idleActions={false} />)
    animate(3000)
    wait(60000)
    expect(paintedSource()).toContain('/mascot/idle.png')
    expect(vi.getTimerCount()).toBe(0)
  })

  it('respects reduced motion initially and when preferences change during an action', () => {
    reduced = true
    render(<MascotSprite pose="idle" idleActions />)
    wait(60000)
    expect(vi.getTimerCount()).toBe(0)
    motion(false)
    wait(13000)
    expect(paintedSource()).toContain('/mascot/random.png')
    motion(true)
    animate(3000)
    wait(60000)
    expect(paintedSource()).toContain('/mascot/idle.png')
    expect(paintedPosition()).toEqual([0, 0])
    expect(vi.getTimerCount()).toBe(0)
  })

  it('waits afresh after a hidden tab and removes scheduled work on unmount', () => {
    const view = render(<MascotSprite pose="idle" idleActions />)
    wait(6000)
    visibility(true)
    wait(60000)
    expect(vi.getTimerCount()).toBe(0)
    visibility(false)
    wait(12999)
    expect(paintedSource()).toContain('/mascot/idle.png')
    wait(1)
    expect(paintedSource()).toContain('/mascot/random.png')
    visibility(true)
    expect(paintedSource()).toContain('/mascot/idle.png')
    visibility(false)
    view.unmount()
    visibility(false)
    motion(false)
    expect(vi.getTimerCount()).toBe(0)
    expect(frames.size).toBe(0)
  })
})
