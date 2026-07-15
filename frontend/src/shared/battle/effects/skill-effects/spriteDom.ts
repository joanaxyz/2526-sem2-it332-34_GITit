import type { SpriteAnimation } from '@/shared/sprites/types'

import type { SpriteAnchor } from './types'

export const CENTER_ANCHOR: SpriteAnchor = { x: 0.5, y: 0.5 }
export const PROJECTILE_NOSE_ANCHOR: SpriteAnchor = { x: 0.78, y: 0.52 }
// The point on a projectile sprite that sits at the caster's hand: the spell
// charges and launches with its body extending FORWARD (into the open space past
// the hand) rather than centered on the caster, so it never overlaps him.
export const PROJECTILE_ORIGIN_ANCHOR: SpriteAnchor = { x: 0.24, y: 0.5 }
export const MISS_LANDING_ANCHOR: SpriteAnchor = { x: 0.47, y: 0.7 }
// Ground-rooted effects are baked with their visible base planted on this line
// (GROUND_ANCHOR_Y / FRAME in process_companion_spell_sheets.py). Placing this
// anchor on the enemy's ground point sits geysers, tornadoes, rings, the push
// shockwave and the switch wave on the floor instead of the enemy's head.
export const FEET_ANCHOR: SpriteAnchor = { x: 0.5, y: 0.86 }

export function reduceMotion(): boolean {
  return (
    typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

export function finishAnimation(animation: Animation, ms: number): Promise<void> {
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

function paintFrame(node: HTMLElement, sheet: SpriteAnimation, frame: number) {
  const col = frame % sheet.columns
  const row = Math.floor(frame / sheet.columns)
  const x = sheet.columns > 1 ? (col * 100) / (sheet.columns - 1) : 0
  const y = sheet.rows > 1 ? (row * 100) / (sheet.rows - 1) : 0
  node.style.backgroundPosition = `${x}% ${y}%`
}

export function animateSheet(node: HTMLElement, sheet: SpriteAnimation, durationMs: number): Promise<void> {
  return new Promise((resolve) => {
    const started = performance.now()
    paintFrame(node, sheet, 0)
    const step = (now: number) => {
      const progress = Math.min(1, (now - started) / durationMs)
      const frame =
        progress >= 1 ? sheet.frameCount - 1 : Math.min(sheet.frameCount - 1, Math.floor(progress * sheet.frameCount))
      paintFrame(node, sheet, frame)
      if (progress < 1) {
        requestAnimationFrame(step)
      } else {
        resolve()
      }
    }
    requestAnimationFrame(step)
  })
}

export function animateFrameRange(
  node: HTMLElement,
  sheet: SpriteAnimation,
  fromFrame: number,
  toFrame: number,
  durationMs: number,
): Promise<void> {
  return new Promise((resolve) => {
    const from = Math.max(0, Math.min(sheet.frameCount - 1, fromFrame))
    const to = Math.max(from, Math.min(sheet.frameCount - 1, toFrame))
    const frameCount = to - from + 1
    const started = performance.now()
    paintFrame(node, sheet, from)
    const step = (now: number) => {
      const progress = Math.min(1, (now - started) / Math.max(1, durationMs))
      const frame = progress >= 1 ? to : Math.min(to, from + Math.floor(progress * frameCount))
      paintFrame(node, sheet, frame)
      if (progress < 1) {
        requestAnimationFrame(step)
      } else {
        resolve()
      }
    }
    requestAnimationFrame(step)
  })
}

export function spriteNode(
  layer: HTMLElement,
  sheetDef: SpriteAnimation,
  options: { scale: number; opacity?: number; filter?: string; pixelated?: boolean },
): HTMLDivElement {
  const node = document.createElement('div')
  const w = sheetDef.frameWidth * options.scale
  const h = sheetDef.frameHeight * options.scale
  node.className = 'battle-skill-effect-sprite'
  node.dataset.effectSprite = sheetDef.name
  Object.assign(node.style, {
    position: 'absolute',
    left: '0',
    top: '0',
    width: `${w}px`,
    height: `${h}px`,
    pointerEvents: 'none',
    userSelect: 'none',
    backgroundImage: `url(${sheetDef.src})`,
    backgroundRepeat: 'no-repeat',
    backgroundSize: `${sheetDef.columns * 100}% ${sheetDef.rows * 100}%`,
    backgroundPosition: '0% 0%',
    imageRendering: options.pixelated ? 'pixelated' : 'auto',
    opacity: `${options.opacity ?? 1}`,
    filter: options.filter ?? '',
    willChange: 'transform, opacity, background-position',
  } satisfies Partial<CSSStyleDeclaration>)
  layer.appendChild(node)
  return node
}

export function flipAnchor(anchor: SpriteAnchor): SpriteAnchor {
  return { x: 1 - anchor.x, y: anchor.y }
}

/**
 * Largest scale factor <= 1 that keeps a sprite of size (w, h), placed so its
 * `anchor` point lands at layer-local `to`, fully inside `host` with `margin`
 * breathing room. The battle stage is `overflow: hidden`, so a target/ground
 * effect scaled up to a big boss near the stage edge would otherwise be cropped
 * at the top/right rather than shrunk to fit. Returns 1 when it already fits.
 */
export function fitScaleToHost(
  host: HTMLElement,
  to: { x: number; y: number },
  anchor: SpriteAnchor,
  w: number,
  h: number,
  margin = 8,
): number {
  const box = host.getBoundingClientRect()
  const W = box.width
  const H = box.height
  if (!W || !H || !w || !h) return 1
  // A short scale-up (fade keyframes reach 1.02) plus the margin keep the top
  // fringe of tall pillars from just kissing the edge.
  const ew = w * 1.03
  const eh = h * 1.03
  const caps: number[] = [1]
  if (anchor.x > 0) caps.push((to.x - margin) / (ew * anchor.x))
  if (anchor.x < 1) caps.push((W - margin - to.x) / (ew * (1 - anchor.x)))
  if (anchor.y > 0) caps.push((to.y - margin) / (eh * anchor.y))
  if (anchor.y < 1) caps.push((H - margin - to.y) / (eh * (1 - anchor.y)))
  const s = Math.min(...caps)
  return s > 0 && s < 1 ? s : 1
}

export function containSpriteInHost(
  host: HTMLElement,
  point: { x: number; y: number },
  anchor: SpriteAnchor,
  w: number,
  h: number,
  opts: { margin?: number; grow?: number; minScaleBeforeShift?: number } = {},
): { point: { x: number; y: number }; scale: number } {
  return containSpriteInHostForAnchors(host, point, [anchor], w, h, opts)
}

export function containSpriteInHostForAnchors(
  host: HTMLElement,
  point: { x: number; y: number },
  anchors: SpriteAnchor[],
  w: number,
  h: number,
  opts: { margin?: number; grow?: number; minScaleBeforeShift?: number } = {},
): { point: { x: number; y: number }; scale: number } {
  const box = host.getBoundingClientRect()
  const W = box.width
  const H = box.height
  if (!W || !H || !w || !h) return { point, scale: 1 }

  const margin = opts.margin ?? 8
  const grow = opts.grow ?? 1.03
  const minScaleBeforeShift = opts.minScaleBeforeShift ?? 0.55
  const ew = w * grow
  const eh = h * grow
  const extents = anchorExtents(anchors)
  const caps: number[] = [1]

  if (extents.left > 0) caps.push((point.x - margin) / (ew * extents.left))
  if (extents.right > 0) caps.push((W - margin - point.x) / (ew * extents.right))
  if (extents.top > 0) caps.push((point.y - margin) / (eh * extents.top))
  if (extents.bottom > 0) caps.push((H - margin - point.y) / (eh * extents.bottom))

  const scaleAtPoint = Math.min(...caps)
  if (scaleAtPoint >= minScaleBeforeShift) {
    return { point, scale: Math.min(1, scaleAtPoint) }
  }

  const wholeHostScale = Math.min(1, (W - margin * 2) / ew, (H - margin * 2) / eh)
  const scale = wholeHostScale > 0 ? wholeHostScale : 1
  const scaledW = ew * scale
  const scaledH = eh * scale
  return {
    point: {
      x: clampAnchorPoint(point.x, margin + scaledW * extents.left, W - margin - scaledW * extents.right, W / 2),
      y: clampAnchorPoint(point.y, margin + scaledH * extents.top, H - margin - scaledH * extents.bottom, H / 2),
    },
    scale,
  }
}

function anchorExtents(anchors: SpriteAnchor[]): { left: number; right: number; top: number; bottom: number } {
  const list = anchors.length ? anchors : [CENTER_ANCHOR]
  return list.reduce(
    (max, anchor) => ({
      left: Math.max(max.left, anchor.x),
      right: Math.max(max.right, 1 - anchor.x),
      top: Math.max(max.top, anchor.y),
      bottom: Math.max(max.bottom, 1 - anchor.y),
    }),
    { left: 0, right: 0, top: 0, bottom: 0 },
  )
}

function clampAnchorPoint(value: number, min: number, max: number, fallback: number): number {
  if (min > max) return fallback
  return Math.min(max, Math.max(min, value))
}

export function placeAt(
  point: { x: number; y: number },
  size: { w: number; h: number },
  anchor: SpriteAnchor,
  extra = '',
): string {
  return `translate(${point.x - size.w * anchor.x}px, ${point.y - size.h * anchor.y}px)${extra}`
}

export function travelRotation(from: { x: number; y: number }, to: { x: number; y: number }): number {
  return Math.atan2(to.y - from.y, to.x - from.x)
}
