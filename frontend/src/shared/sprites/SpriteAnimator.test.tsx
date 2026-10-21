import { createRef } from 'react'
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

const { getWarmedImageMock, warmImageMock } = vi.hoisted(() => ({
  getWarmedImageMock: vi.fn(),
  warmImageMock: vi.fn(),
}))

vi.mock('@/shared/sprites/preload', () => ({
  getWarmedImage: getWarmedImageMock,
  warmImage: warmImageMock,
}))

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
let images: Map<string, HTMLImageElement>
const clearRect = vi.fn()
const drawImage = vi.fn()

beforeEach(() => {
  now = 0
  reducedMotion = false
  motionChanges = new EventTarget()
  frames = new Map()
  images = new Map(['/idle.png', '/attack.png'].map((src) => {
    const image = document.createElement('img')
    image.src = src
    return [src, image]
  }))
  getWarmedImageMock.mockImplementation((src: string) => images.get(src) ?? null)
  warmImageMock.mockReset().mockResolvedValue(undefined)
  clearRect.mockClear()
  drawImage.mockClear()
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
    clearRect, drawImage, imageSmoothingEnabled: false,
  } as unknown as CanvasRenderingContext2D)
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
  it('commits a new sheet, dimensions and starting frame in one imperative paint', () => {
    const ref = createRef<SpriteAnimatorHandle>()
    render(<SpriteAnimator ref={ref} animation={idle} layoutAnimation={idle} autoPlay={false} />)
    const sprite = screen.getByRole('img').firstElementChild as HTMLCanvasElement
    const resize = vi.spyOn(sprite, 'width', 'set')
    const largeAttack = { ...attack, frameWidth: 64, frameHeight: 64 }

    act(() => {
      ref.current?.setAnimation(largeAttack, { segment: { from: 3, to: 3 } })
      // The new source and crop must agree before React commits the new pose.
      expect(sprite.width).toBe(64)
      expect(sprite.height).toBe(64)
      expect(drawImage).toHaveBeenLastCalledWith(images.get('/attack.png'), 64, 64, 64, 64, 0, 0, 64, 64)
    })

    expect(drawImage).toHaveBeenLastCalledWith(images.get('/attack.png'), 64, 64, 64, 64, 0, 0, 64, 64)
    // A React width attribute commit would clear the freshly painted canvas.
    expect(resize).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('img')).toHaveStyle({ width: '32px', height: '32px' })
  })

  it('paints the current frame when a cold sheet finishes decoding', async () => {
    let finishDecode!: () => void
    const decoded = new Promise<void>((resolve) => { finishDecode = resolve })
    warmImageMock.mockImplementation((src: string) => src === '/slow.png' ? decoded : Promise.resolve())
    const ref = createRef<SpriteAnimatorHandle>()
    render(<SpriteAnimator ref={ref} animation={idle} />)
    act(() => {
      ref.current?.setAnimation({ ...attack, src: '/slow.png' })
      ref.current?.pause()
      ref.current?.goToFrame(2)
    })

    const image = document.createElement('img')
    image.src = '/slow.png'
    images.set('/slow.png', image)
    await act(async () => { finishDecode(); await decoded })

    expect(drawImage).toHaveBeenLastCalledWith(image, 0, 32, 32, 32, 0, 0, 32, 32)
    expect(ref.current?.isPlaying()).toBe(false)
  })

  it('does not let a late image load overwrite a newer pose', async () => {
    let finishDecode!: () => void
    const decoded = new Promise<void>((resolve) => { finishDecode = resolve })
    warmImageMock.mockImplementation((src: string) => src === '/late.png' ? decoded : Promise.resolve())
    const ref = createRef<SpriteAnimatorHandle>()
    render(<SpriteAnimator ref={ref} animation={idle} />)
    act(() => ref.current?.setAnimation({ ...idle, src: '/late.png' }))
    act(() => ref.current?.setAnimation(attack))
    const paints = drawImage.mock.calls.length
    images.set('/late.png', document.createElement('img'))
    await act(async () => { finishDecode(); await decoded })

    expect(drawImage.mock.calls.slice(paints).every(([image]) => image === images.get('/attack.png'))).toBe(true)
    expect(drawImage).toHaveBeenLastCalledWith(images.get('/attack.png'), 0, 0, 32, 32, 0, 0, 32, 32)
  })

  it.each([
    { label: 'Blue', frameWidth: 253, frameHeight: 244, scale: 0.78 },
    { label: 'Arcane hound', frameWidth: 244, frameHeight: 193, scale: 0.99 },
    { label: 'Neon hound', frameWidth: 239, frameHeight: 182, scale: 1.09 },
    { label: 'Bone Soldier', frameWidth: 243, frameHeight: 194, scale: 0.87 },
    { label: 'Neon soldier', frameWidth: 243, frameHeight: 200, scale: 1.04 },
  ])('paints $label into a fixed native canvas before display scaling', ({ frameWidth, frameHeight, scale }) => {
    const ref = createRef<SpriteAnimatorHandle>()
    const sheet = { ...idle, frameWidth, frameHeight, columns: 5, rows: 5, frameCount: 25 }
    render(<SpriteAnimator ref={ref} animation={sheet} scale={scale} autoPlay={false} />)
    const sprite = screen.getByRole('img').firstElementChild as HTMLCanvasElement

    expect(screen.getByRole('img')).toHaveStyle({
      width: `${frameWidth * scale}px`, height: `${frameHeight * scale}px`,
    })
    expect(sprite.width).toBe(frameWidth)
    expect(sprite.height).toBe(frameHeight)
    expect(sprite.style.backgroundImage).toBe('')
    expect(sprite.style.transform).toBe('')

    for (let frame = 0; frame < 25; frame += 1) {
      act(() => ref.current?.goToFrame(frame))
      expect(clearRect).toHaveBeenLastCalledWith(0, 0, frameWidth, frameHeight)
      expect(drawImage).toHaveBeenLastCalledWith(
        images.get('/idle.png'), (frame % 5) * frameWidth, Math.floor(frame / 5) * frameHeight,
        frameWidth, frameHeight, 0, 0, frameWidth, frameHeight,
      )
      expect(sprite.width).toBe(frameWidth)
      expect(sprite.height).toBe(frameHeight)
    }
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
    expect(drawImage.mock.lastCall?.slice(1, 3)).not.toEqual([0, 0])
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
