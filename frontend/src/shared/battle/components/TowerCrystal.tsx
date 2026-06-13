import { forwardRef, useImperativeHandle, useRef } from 'react'

import { cn } from '@/shared/utils/cn'

export type TowerCrystalHandle = {
  /** A monster blow landed on the tower: jolt + flare, crystal survives. */
  shake: () => Promise<void>
  /** Mana spent — the crystal cracks and goes dark (defeat). */
  shatter: () => void
  /** Restore for the next level. */
  reset: () => void
  element: () => HTMLDivElement | null
}

/**
 * The tower crystal Blue defends: a floating arcane gem on the ledge. It has no
 * HP of its own — misses are pure drama (a jolt) — but it shatters the moment
 * mana runs out, which is the run's defeat. Compositor-only verbs (transform /
 * opacity), so nothing here triggers layout mid-battle.
 */
export const TowerCrystal = forwardRef<TowerCrystalHandle, { scale?: number; className?: string }>(
  function TowerCrystal({ scale = 1, className }, ref) {
    const wrapRef = useRef<HTMLDivElement | null>(null)
    const gemRef = useRef<HTMLDivElement | null>(null)

    useImperativeHandle(ref, () => ({
      shake: () =>
        new Promise<void>((resolve) => {
          const node = wrapRef.current
          const gem = gemRef.current
          gem?.animate(
            [
              { filter: 'brightness(1)' },
              { filter: 'brightness(1.9)', offset: 0.2 },
              { filter: 'brightness(1)' },
            ],
            { duration: 460, easing: 'ease-out' },
          )
          if (!node) return resolve()
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

      shatter: () => {
        const gem = gemRef.current
        if (!gem) return
        gem.classList.add('tower-crystal--broken')
        gem.animate(
          [
            { transform: 'scale(1)', opacity: 1 },
            { transform: 'scale(1.15)', opacity: 1, offset: 0.15 },
            { transform: 'scale(0.6) rotate(8deg)', opacity: 0 },
          ],
          { duration: 620, easing: 'cubic-bezier(0.4, 0, 0.2, 1)', fill: 'forwards' },
        )
      },

      reset: () => {
        const gem = gemRef.current
        if (!gem) return
        gem.classList.remove('tower-crystal--broken')
        gem.style.transform = ''
        gem.style.opacity = ''
      },

      element: () => wrapRef.current,
    }))

    return (
      <div
        ref={wrapRef}
        className={cn('tower-crystal pointer-events-none relative', className)}
        style={{ width: 30 * scale, height: 46 * scale }}
        aria-hidden
      >
        <div ref={gemRef} className="tower-crystal-gem" />
        <span className="tower-crystal-base" />
      </div>
    )
  },
)
