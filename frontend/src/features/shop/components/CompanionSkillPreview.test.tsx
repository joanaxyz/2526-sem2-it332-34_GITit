import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CompanionSkillPreview } from './CompanionCombatPreview'

vi.mock('@/shared/sprites/SpriteAnimator', () => ({
  SpriteAnimator: ({ scale, 'aria-label': label }: { scale: number; 'aria-label': string }) => (
    <div role="img" aria-label={label} style={{ width: 256 * scale, height: 256 * scale }} />
  ),
}))

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('CompanionSkillPreview', () => {
  it('fits the full frame in a short or narrow stage and responds to resizing', () => {
    let resize: ResizeObserverCallback = () => undefined
    const disconnect = vi.fn()
    vi.stubGlobal('ResizeObserver', class {
      constructor(callback: ResizeObserverCallback) { resize = callback }
      observe = vi.fn()
      disconnect = disconnect
    })
    const { unmount } = render(<CompanionSkillPreview companionSlug="white" />)
    const sprite = screen.getByRole('img', { name: 'git init skill effect' })
    const resizeStage = (width: number, height: number) => act(() => {
      resize([{ contentRect: { width, height } } as ResizeObserverEntry], {} as ResizeObserver)
    })

    resizeStage(420, 180)
    expect(Number.parseFloat(sprite.style.height)).toBeLessThan(180)
    expect(sprite.style.width).toBe(sprite.style.height)

    resizeStage(150, 300)
    expect(Number.parseFloat(sprite.style.width)).toBeLessThan(150)
    expect(sprite.style.width).toBe(sprite.style.height)

    resizeStage(600, 400)
    expect(sprite.style.width).toBe('236px')
    expect(sprite.style.height).toBe('236px')

    unmount()
    expect(disconnect).toHaveBeenCalledOnce()
  })
})
