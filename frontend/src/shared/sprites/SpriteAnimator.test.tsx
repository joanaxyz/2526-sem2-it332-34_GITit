import { createRef } from 'react'
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

const idle: SpriteAnimation = {
  name: 'hero.idle',
  src: '/idle.png',
  frameWidth: 32,
  frameHeight: 32,
  columns: 4,
  rows: 1,
  frameCount: 4,
  fps: 8,
  loop: true,
}

const attack: SpriteAnimation = {
  name: 'hero.attack',
  src: '/attack.png',
  frameWidth: 32,
  frameHeight: 32,
  columns: 2,
  rows: 2,
  frameCount: 4,
  fps: 12,
  loop: false,
}

let now = 0
let reducedMotion = false
let motionChanges: EventTarget
let frames: Map<number, FrameRequestCallback>

beforeEach(() => {
  now = 0
  reducedMotion = false
  motionChanges = new EventTarget()
  frames = new Map()
  let id = 0
  vi.spyOn(performance, 'now').mockImplementation(() => now)
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    frames.set(++id, callback)
    return id
  })
  vi.stubGlobal('cancelAnimationFrame', (frame: number) => frames.delete(frame))
  vi.stubGlobal('matchMedia', () => ({
    get matches() { return reducedMotion },
    addEventListener: motionChanges.addEventListener.bind(motionChanges),
    removeEventListener: motionChanges.removeEventListener.bind(motionChanges),
  }))
})

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

function advance(milliseconds: number) {
  act(() => {
    for (let elapsed = 0; elapsed < milliseconds; elapsed += 10) {
      now += 10
      const pending = [...frames.values()]
      frames.clear()
      pending.forEach((callback) => callback(now))
    }
  })
}

function setReducedMotion(reduced: boolean) {
  act(() => {
    reducedMotion = reduced
    motionChanges.dispatchEvent(new Event('change'))
  })
}

describe('SpriteAnimator', () => {
  it('commits a new sheet, grid and starting frame in one imperative paint', () => {
    const ref = createRef<SpriteAnimatorHandle>()
    render(<SpriteAnimator ref={ref} animation={idle} autoPlay={false} />)
    const sprite = screen.getByRole('img').firstElementChild as HTMLElement

    act(() => {
      ref.current?.setAnimation(attack, { segment: { from: 3, to: 3 } })
      // Assert before act flushes React's state update: these styles must already
      // agree or the browser can expose one frame from the old sheet/grid.
      expect(sprite.style.backgroundImage).toContain('attack.png')
      expect(sprite.style.backgroundSize).toBe('200% 200%')
      expect(sprite.style.backgroundPosition).toBe('100% 100%')
    })

    expect(sprite.style.backgroundPosition).toBe('100% 100%')
  })

  it.each([idle, attack])('plays $name after the previous one-shot finishes', (next) => {
    const ref = createRef<SpriteAnimatorHandle>()
    const view = render(<SpriteAnimator ref={ref} animation={attack} />)
    advance(500)
    expect(ref.current?.isPlaying()).toBe(false)
    expect(ref.current?.getFrame()).toBe(3)

    // A new pose can reuse the same sheet with a new animation definition.
    view.rerender(<SpriteAnimator ref={ref} animation={{ ...next }} />)
    expect(ref.current?.getFrame()).toBe(0)
    expect(ref.current?.isPlaying()).toBe(true)
    advance(150)
    expect(ref.current?.getFrame()).toBeGreaterThan(0)
    expect((screen.getByRole('img').firstElementChild as HTMLElement).style.backgroundPosition).not.toBe('0% 0%')
  })

  it('keeps prop-driven animation changes paused when autoplay is disabled', () => {
    const ref = createRef<SpriteAnimatorHandle>()
    const view = render(<SpriteAnimator ref={ref} animation={idle} autoPlay={false} />)
    view.rerender(<SpriteAnimator ref={ref} animation={attack} autoPlay={false} />)
    advance(500)
    expect(ref.current?.isPlaying()).toBe(false)
    expect(ref.current?.getFrame()).toBe(0)
    act(() => ref.current?.play())
    advance(150)
    expect(ref.current?.getFrame()).toBeGreaterThan(0)
  })

  it('discards a stale completion callback when a prop replaces an imperative animation', () => {
    const ref = createRef<SpriteAnimatorHandle>()
    const onComplete = vi.fn()
    const view = render(<SpriteAnimator ref={ref} animation={idle} />)
    act(() => ref.current?.setAnimation(attack, { onComplete }))
    view.rerender(<SpriteAnimator ref={ref} animation={{ ...attack, name: 'hero.land' }} />)
    advance(500)
    expect(ref.current?.isPlaying()).toBe(false)
    expect(onComplete).not.toHaveBeenCalled()
  })

  it('resumes when reduced motion is disabled and holds the first frame when enabled', () => {
    reducedMotion = true
    const ref = createRef<SpriteAnimatorHandle>()
    render(<SpriteAnimator ref={ref} animation={idle} />)
    advance(250)
    expect(ref.current?.getFrame()).toBe(0)
    setReducedMotion(false)
    advance(150)
    expect(ref.current?.getFrame()).toBeGreaterThan(0)
    setReducedMotion(true)
    advance(250)
    expect(ref.current?.getFrame()).toBe(0)
  })

  it('preserves an explicit pause across motion preference changes and cleans up on unmount', () => {
    const ref = createRef<SpriteAnimatorHandle>()
    const view = render(<SpriteAnimator ref={ref} animation={idle} autoPlay={false} />)
    setReducedMotion(true)
    setReducedMotion(false)
    advance(250)
    expect(ref.current?.isPlaying()).toBe(false)
    expect(ref.current?.getFrame()).toBe(0)
    view.unmount()
    setReducedMotion(true)
    setReducedMotion(false)
    expect(frames.size).toBe(0)
  })
})
