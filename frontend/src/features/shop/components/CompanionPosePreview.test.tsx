import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CompanionPosePreview } from './CompanionCombatPreview'

vi.mock('@/shared/sprites/SpriteAnimator', () => ({
  SpriteAnimator: ({ scale, layoutAnimation, 'aria-label': label }: {
    scale: number
    layoutAnimation: { frameWidth: number; frameHeight: number; displayScale?: number }
    'aria-label': string
  }) => (
    <div
      role="img"
      aria-label={label}
      data-scale={scale}
      style={{
        width: layoutAnimation.frameWidth * (layoutAnimation.displayScale ?? 1) * scale,
        height: layoutAnimation.frameHeight * (layoutAnimation.displayScale ?? 1) * scale,
      }}
    />
  ),
}))

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('CompanionPosePreview', () => {
  it('fits the anchored pose in a short or narrow stage and responds to resizing', () => {
    let resize: ResizeObserverCallback = () => undefined
    const disconnect = vi.fn()
    vi.stubGlobal('ResizeObserver', class {
      constructor(callback: ResizeObserverCallback) { resize = callback }
      observe = vi.fn()
      disconnect = disconnect
    })
    const { unmount } = render(<CompanionPosePreview companionSlug="blue" />)
    const resizeStage = (width: number, height: number) => act(() => {
      resize([{ contentRect: { width, height } } as ResizeObserverEntry], {} as ResizeObserver)
    })
    const sprite = screen.getByRole('img', { name: 'Blue Idle' })

    resizeStage(420, 180)
    expect(Number.parseFloat(sprite.style.height) + 19 * Number(sprite.dataset.scale)).toBeLessThanOrEqual(164)

    resizeStage(150, 300)
    expect(Number.parseFloat(sprite.style.width)).toBeLessThanOrEqual(134)

    resizeStage(600, 400)
    expect(Number.parseFloat(sprite.style.height) + 19 * Number(sprite.dataset.scale)).toBeCloseTo(300)

    fireEvent.click(screen.getByRole('button', { name: 'Next pose' }))
    expect(screen.getByRole('img', { name: 'Blue Run' }).dataset.scale).toBe(sprite.dataset.scale)

    unmount()
    expect(disconnect).toHaveBeenCalledOnce()
  })
})
