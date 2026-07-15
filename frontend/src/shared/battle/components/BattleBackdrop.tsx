import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'

import { cn } from '@/shared/utils/cn'

const PARALLAX_SCROLL_SCALE = 1

export type BattleBackdropHandle = {
  /** Scroll the horizontal parallax by `px`; offsets are cumulative. */
  scroll: (px: number, ms?: number) => Promise<void>
}

function positionXForOffset(offset: number) {
  return `calc(50% - ${offset}px)`
}

function finishAnimation(animation: Animation, ms: number): Promise<void> {
  return Promise.race([
    animation.finished.then(
      () => undefined,
      () => undefined,
    ),
    new Promise<void>((resolve) => {
      window.setTimeout(resolve, ms + 120)
    }),
  ])
}

/**
 * Battle backdrop: the active run can select a chapter parallax, and adventure
 * travel pans the repeat-x background, so offsets can accumulate forever.
 */
export const BattleBackdrop = forwardRef<
  BattleBackdropHandle,
  { parallaxUrl?: string | null; scrollEnabled?: boolean; className?: string }
>(function BattleBackdrop({ parallaxUrl, scrollEnabled = true, className }, ref) {
  const parallaxRef = useRef<HTMLDivElement>(null)
  const offsetRef = useRef(0)

  useEffect(() => {
    offsetRef.current = 0
    if (parallaxRef.current) parallaxRef.current.style.backgroundPositionX = positionXForOffset(0)
  }, [parallaxUrl])

  useImperativeHandle(ref, () => ({
    scroll: async (px: number, ms = 760) => {
      const parallax = parallaxRef.current
      if (!parallax || !scrollEnabled) return

      const from = offsetRef.current
      const to = from + px * PARALLAX_SCROLL_SCALE
      offsetRef.current = to
      const animation = parallax.animate(
        [{ backgroundPositionX: positionXForOffset(from) }, { backgroundPositionX: positionXForOffset(to) }],
        { duration: ms, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
      )
      await finishAnimation(animation, ms)
      parallax.style.backgroundPositionX = positionXForOffset(to)
      animation.cancel()
    },
  }))

  return (
    <div className={cn('pointer-events-none absolute inset-0 overflow-hidden', className)} aria-hidden>
      <div
        ref={parallaxRef}
        className={cn('battle-parallax-layer absolute inset-0', !parallaxUrl && 'battle-parallax-fallback')}
        style={parallaxUrl ? { backgroundImage: `url("${parallaxUrl}")` } : undefined}
      />
    </div>
  )
})
