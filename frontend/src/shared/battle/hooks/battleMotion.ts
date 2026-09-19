export const TRAVEL_SCROLL_PX = 460
export const TRAVEL_SCROLL_MS = 1100
export const RUN_IN_SCROLL_MIN_PX = 160
export const RUN_IN_SCROLL_SCALE = 0.72
export const CENTER_SCROLL_FRAC = 0.38
export const CENTER_SCROLL_MS = 820
// Fraction of Blue's closing run the camera drifts to follow him (0 = static
// camera, 1 = fully locked on Blue). A partial follow keeps him advancing on
// screen while the world visibly pans past.
export const CAMERA_FOLLOW_FRAC = 0.5
export const MONSTER_PEEK_MS = 540
export const MONSTER_ENTRY_STAGGER_MS = 100
export const SIGHTED_IDLE_PAUSE_MS = 180
export const MONSTER_PEEK_VISIBLE = 0.42
export const PEEK_START_FRAC = 0.52

export function readTranslateX(node: HTMLElement): number {
  const inline = node.style.transform
  const match = /translate(?:X)?\(([-\d.]+)px/.exec(inline)
  if (match) return Number(match[1])
  const matrix = window.getComputedStyle(node).transform
  if (matrix && matrix !== 'none') {
    const parts = matrix.match(/matrix\(([^)]+)\)/)
    if (parts) {
      const values = parts[1].split(',').map((v) => Number.parseFloat(v.trim()))
      if (values.length === 6) return values[4]
    }
  }
  return 0
}

/**
 * Source of truth for "should battle choreography skip its animated steps."
 * Reads the app's own resolved motion preference (`data-motion`, set by
 * `applyPreferences` in `shared/preferences/preferences.ts`) rather than
 * querying the OS media query directly — that resolved value already folds
 * in the OS `prefers-reduced-motion` setting as the fallback for "system",
 * so checking it here keeps this in sync with the in-app Motion setting
 * (Settings page) that CSS already respects via `:root[data-motion='reduced']`.
 */
export function isMotionReduced(): boolean {
  return document.documentElement.dataset.motion === 'reduced'
}

export function boundedAnimation(promise: Promise<void>, ms: number): Promise<void> {
  return Promise.race([
    promise,
    new Promise<void>((resolve) => {
      window.setTimeout(resolve, ms)
    }),
  ])
}

export function wait(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

export function nextPaint(): Promise<void> {
  return new Promise((resolve) => {
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      resolve()
    }
    requestAnimationFrame(finish)
    window.setTimeout(finish, 80)
  })
}

export function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value))
}

