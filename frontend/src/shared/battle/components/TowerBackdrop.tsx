import { forwardRef, useImperativeHandle, useRef } from 'react'

import { cn } from '@/shared/utils/cn'

export type TowerBackdropHandle = {
  /**
   * Pan the star/cloud field downward over `ms` to sell Blue rising a floor -
   * the vertical counterpart of the old horizontal parallax travel. Offsets are
   * cumulative so successive climbs keep flowing on the repeating tiles.
   */
  climb: (ms: number) => Promise<void>
}

/**
 * The tower-defense sky: a living gradient + sun/moon arc driven by the sky CSS
 * vars the stage sets (computeSky), drifting clouds, and a repeating star
 * field. Pure CSS layers; the only scripted motion is the climb pan via WAAPI.
 * The sky echoes the /tower page so a battle reads as one floor of the tower.
 */
export const TowerBackdrop = forwardRef<TowerBackdropHandle, { className?: string }>(
  function TowerBackdrop({ className }, ref) {
    const starsRef = useRef<HTMLDivElement>(null)
    const cloudsRef = useRef<HTMLDivElement>(null)
    const offsetRef = useRef({ stars: 0, clouds: 0 })

    useImperativeHandle(ref, () => ({
      climb: async (ms: number) => {
        const layers: Array<[HTMLDivElement | null, 'stars' | 'clouds', number]> = [
          [starsRef.current, 'stars', 0.5],
          [cloudsRef.current, 'clouds', 1],
        ]
        const animations = layers.flatMap(([node, key, speed]) => {
          if (!node) return []
          const from = offsetRef.current[key]
          const to = from + 260 * speed
          offsetRef.current[key] = to
          const animation = node.animate(
            [{ backgroundPositionY: `${from}px` }, { backgroundPositionY: `${to}px` }],
            { duration: ms, easing: 'cubic-bezier(0.45, 0, 0.25, 1)', fill: 'forwards' },
          )
          return [
            animation.finished.then(() => {
              node.style.backgroundPositionY = `${to}px`
              animation.cancel()
            }),
          ]
        })
        await Promise.allSettled(animations)
      },
    }))

    return (
      <div className={cn('pointer-events-none absolute inset-0 overflow-hidden', className)} aria-hidden>
        {/* Living sky gradient + ambient glow, both from the sky CSS vars. */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(120% 80% at 50% 110%, rgba(var(--sky-glow), 0.30), transparent 60%),' +
              'linear-gradient(to bottom, var(--sky-top), var(--sky-mid) 55%, var(--sky-bottom) 100%)',
          }}
        />
        {/* Sun and moon ride the same arc as the tower page. */}
        <div
          className="absolute size-14 rounded-full"
          style={{
            left: 'var(--sun-x, 80%)',
            top: 'var(--sun-y, 30%)',
            opacity: 'var(--sun-opacity, 0)',
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(circle, #fff7e0 0%, #ffd27a 45%, rgba(255,180,90,0) 72%)',
            filter: 'blur(0.5px)',
          }}
        />
        <div
          className="absolute size-10 rounded-full"
          style={{
            left: 'var(--moon-x, 20%)',
            top: 'var(--moon-y, 30%)',
            opacity: 'var(--moon-opacity, 1)',
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(circle at 38% 38%, #f4f7ff 0%, #c8d2f0 55%, rgba(150,165,210,0) 75%)',
          }}
        />
        {/* Star field: repeating tile so the climb pan loops seamlessly. */}
        <div
          ref={starsRef}
          className="absolute inset-0"
          style={{
            opacity: 'var(--star-opacity, 1)',
            backgroundImage:
              'radial-gradient(1px 1px at 18% 30%, rgba(255,255,255,0.9), transparent 60%),' +
              'radial-gradient(1.4px 1.4px at 52% 14%, rgba(200,225,255,0.8), transparent 60%),' +
              'radial-gradient(1px 1px at 74% 38%, rgba(255,255,255,0.7), transparent 60%),' +
              'radial-gradient(1px 1px at 88% 18%, rgba(220,200,255,0.7), transparent 60%),' +
              'radial-gradient(1px 1px at 34% 60%, rgba(255,255,255,0.6), transparent 60%)',
            backgroundSize: '100% 300px',
            backgroundRepeat: 'repeat',
          }}
        />
        {/* Drifting nebula clouds, tinted by the sky vars. */}
        <div
          ref={cloudsRef}
          className="battle-clouds absolute inset-0"
          style={{
            opacity: 'var(--cloud-opacity, 0.5)',
            backgroundImage:
              'radial-gradient(150px 36px at 80px 60px, rgba(var(--sky-glow), 0.16), transparent 70%),' +
              'radial-gradient(190px 44px at 300px 150px, rgba(var(--sky-glow), 0.12), transparent 70%),' +
              'radial-gradient(130px 32px at 460px 240px, rgba(var(--sky-glow), 0.10), transparent 70%)',
            backgroundSize: '520px 320px',
            backgroundRepeat: 'repeat',
          }}
        />
      </div>
    )
  },
)
