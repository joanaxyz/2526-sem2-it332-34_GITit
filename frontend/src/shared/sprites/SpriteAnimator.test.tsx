import { createRef } from 'react'
import { act, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

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
})
