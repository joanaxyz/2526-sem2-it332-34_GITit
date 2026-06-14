import { forwardRef, useImperativeHandle, useRef } from 'react'

import type { CrystalSheets } from '@/shared/sprites/crystal'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimatorHandle } from '@/shared/sprites/types'
import { cn } from '@/shared/utils/cn'

export type TowerCrystalHandle = {
  /** A monster blow landed on the tower: jolt + flare, crystal survives. */
  shake: () => Promise<void>
  /** Mana spent - the crystal plays its shatter sheet and goes dark (defeat). */
  shatter: () => void
  /** Restore for the next level. */
  reset: () => void
  element: () => HTMLDivElement | null
}

/** Base display scale; the stage passes a per-variant multiplier on top. */
const BASE_SCALE = 0.46

/**
 * The crystal Blue defends, planted on the right of the ledge while monsters
 * besiege it. It has no HP of its own - misses are pure drama (a jolt) - but it
 * plays its `defeat` sheet the moment mana runs out, which is the run's defeat.
 * The jolt/flare run as compositor-only WAAPI (transform/filter), so nothing
 * here triggers layout mid-battle.
 */
export const TowerCrystal = forwardRef<
  TowerCrystalHandle,
  { crystal: CrystalSheets; scale?: number; className?: string }
>(function TowerCrystal({ crystal, scale = 1, className }, ref) {
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const finalScale = BASE_SCALE * scale

    useImperativeHandle(ref, () => ({
      shake: () =>
        new Promise<void>((resolve) => {
          const node = wrapRef.current
          if (!node) return resolve()
          // Flare and jolt as separate property animations so they compose.
          node.animate(
            [
              { filter: 'brightness(1)' },
              { filter: 'brightness(1.9)', offset: 0.2 },
              { filter: 'brightness(1)' },
            ],
            { duration: 460, easing: 'ease-out' },
          )
          const jolt = node.animate(
            [
              { transform: 'translateX(0) rotate(0deg)' },
              { transform: 'translateX(-5px) rotate(-3deg)', offset: 0.25 },
              { transform: 'translateX(4px) rotate(2deg)', offset: 0.6 },
              { transform: 'translateX(0) rotate(0deg)' },
            ],
            { duration: 460, easing: 'ease-out' },
          )
          jolt.finished.catch(() => {}).finally(resolve)
        }),

      // Play the shatter sheet once; SpriteAnimator holds its final dark frame.
      shatter: () => {
        spriteRef.current?.setAnimation(crystal.defeat)
      },

      reset: () => {
        spriteRef.current?.setAnimation(crystal.idle)
        const node = wrapRef.current
        if (node) node.style.transform = ''
      },

      element: () => wrapRef.current,
    }))

    return (
      <div
        ref={wrapRef}
        className={cn('tower-crystal pointer-events-none', className)}
        // Source frames pad below the crystal's base; pull it down so it stands
        // on the ledge line instead of floating above it.
        style={{ marginBottom: -crystal.footOffset * finalScale }}
        aria-hidden
      >
        <SpriteAnimator
          ref={spriteRef}
          animation={crystal.idle}
          scale={finalScale}
          className="tower-crystal-sprite"
          aria-label="The tower crystal"
        />
      </div>
    )
  },
)
