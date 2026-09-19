import { useEffect, useState } from 'react'

/**
 * A load short enough to be imperceptible should not flash a loader on the way
 * past. Nothing paints until the wait is real; the container still holds its
 * box so the layout never jumps.
 */
export const LOADING_PAINT_DELAY_MS = 160

/**
 * Past this the wait has stopped looking like a wait and starts looking broken.
 * Long enough that a normal slow request never trips it.
 */
export const LOADING_SLOW_AFTER_MS = 9000

export function useElapsedFlag(afterMs: number) {
  const [elapsed, setElapsed] = useState(false)
  useEffect(() => {
    const timer = window.setTimeout(() => setElapsed(true), afterMs)
    return () => window.clearTimeout(timer)
  }, [afterMs])
  return elapsed
}

/**
 * Body scroll lock, ref-counted.
 *
 * Two loading screens can briefly overlap - one page's overlay still mounted
 * while the next route's goes up. Each storing and restoring
 * `body.style.overflow` on its own leaves the loser's stale value behind, and
 * the page ends up permanently unscrollable. Only the first lock records the
 * original value and only the last one puts it back.
 */
let scrollLocks = 0
let originalOverflow = ''

export function useLockBodyScroll() {
  useEffect(() => {
    if (scrollLocks === 0) {
      originalOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    }
    scrollLocks += 1

    return () => {
      scrollLocks -= 1
      if (scrollLocks === 0) document.body.style.overflow = originalOverflow
    }
  }, [])
}
