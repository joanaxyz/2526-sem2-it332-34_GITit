import { loadSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'
import type { SpriteAnimation } from '@/shared/sprites/types'

/**
 * Session-wide image warming.
 *
 * Decode sheets before the sprite canvas needs its first frame, and backdrops
 * before their CSS background mounts. Keep the decoded images available to the
 * canvas painter so warmed poses can swap synchronously without a blank frame.
 *
 * Caches are keyed by src and retained for the session:
 * `pending` de-duplicates concurrent requests, `warmed` answers "has this
 * already been done" synchronously, and `decodedImages` supplies successful
 * loads to frame painters.
 * A sheet that fails to load counts as warmed: a 404 must not make a loading
 * gate wait for it twice, and the stage renders the same either way.
 */
const pending = new Map<string, Promise<void>>()
const warmed = new Set<string>()
const decodedImages = new Map<string, HTMLImageElement>()

/** The decoded sheet, shared by preload gates and frame painters. */
export function getWarmedImage(src: string): HTMLImageElement | null {
  return decodedImages.get(src) ?? null
}

/** True once `src` has been decoded (or has failed and will not be retried). */
export function isImageWarm(src: string): boolean {
  return warmed.has(src)
}

/** Decode one image into the browser cache. Never rejects. */
export function warmImage(src: string): Promise<void> {
  if (!src) return Promise.resolve()
  if (warmed.has(src)) return Promise.resolve()
  const cached = pending.get(src)
  if (cached) return cached
  if (typeof Image === 'undefined') return Promise.resolve()

  const image = new Image()
  image.decoding = 'async'
  image.src = src
  const loaded =
    typeof image.decode === 'function'
      ? image.decode()
      : new Promise<void>((resolve, reject) => {
          image.onload = () => resolve()
          image.onerror = () => reject(new Error(`Could not warm image ${src}`))
        })

  const settled = loaded.then(
    () => {
      decodedImages.set(src, image)
      warmed.add(src)
    },
    () => {
      // A missing sheet must never wedge the gate that is waiting on it.
      warmed.add(src)
    },
  )
  pending.set(src, settled)
  return settled
}

/**
 * Warm a sheet and, when the surface that renders it aligns visible pixels
 * rather than the transparent frame box (`anchorToPixelBounds`), measure that
 * anchor too. The measurement is what shifts an actor into place; leaving it for
 * mount makes the sprite jump once it lands, which reads as a flicker of its own.
 */
export async function warmSprite(
  sheet: SpriteAnimation,
  options: { measureAnchor?: boolean } = {},
): Promise<void> {
  await warmImage(sheet.src)
  if (options.measureAnchor) await loadSpritePixelAnchor(sheet)
}

/** Warm every source, resolving when all have settled or `timeoutMs` elapses. */
export function warmImages(sources: Iterable<string>, timeoutMs?: number): Promise<void> {
  const all = Promise.all(Array.from(sources, (src) => warmImage(src))).then(() => undefined)
  return withBudget(all, timeoutMs)
}

/**
 * A wait that gives up. Art is worth a pause, never a hostage: past the budget
 * the surface renders with whatever has arrived and the rest keeps loading.
 */
export function withBudget(work: Promise<void>, timeoutMs?: number): Promise<void> {
  if (!timeoutMs || timeoutMs <= 0) return work
  let timer = 0
  const expiry = new Promise<void>((resolve) => {
    timer = window.setTimeout(resolve, timeoutMs)
  })
  return Promise.race([work, expiry]).finally(() => {
    window.clearTimeout(timer)
  })
}
