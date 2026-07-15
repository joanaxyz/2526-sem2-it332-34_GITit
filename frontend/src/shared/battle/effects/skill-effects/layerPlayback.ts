import type { SpriteAnimation } from '@/shared/sprites/types'

import type { SpriteAnchor } from './types'
import {
  CENTER_ANCHOR,
  FEET_ANCHOR,
  PROJECTILE_NOSE_ANCHOR,
  PROJECTILE_ORIGIN_ANCHOR,
  animateFrameRange,
  animateSheet,
  containSpriteInHost,
  containSpriteInHostForAnchors,
  finishAnimation,
  flipAnchor,
  placeAt,
  spriteNode,
} from './spriteDom'

export type ProjectileLayerSpec = {
  host: HTMLElement
  sheet: SpriteAnimation
  scale: number
  from: { x: number; y: number }
  /** Flight target. For ground-impact companion effects this is the body point,
   *  not the floor. */
  to: { x: number; y: number }
  /** Optional impact pin. When supplied, the flight still lands on `to`, and
   *  only the impact/dissipate frames settle here. */
  impactTo?: { x: number; y: number }
  durationMs: number
  impactAnchor?: SpriteAnchor
  impactStartFrame?: number
  opacity?: number
  filter?: string
  pixelated?: boolean
  /** Extra transform appended after placement: travel rotate, or a facing flip. */
  orientation?: string
  onLaunch?: () => void
  onImpact?: () => void
}

// Most projectile sheets end with impact/dissipate frames that should hold on
// the hit point, but the exact boundary is authored per sheet.
const DEFAULT_PROJECTILE_IMPACT_START_FRAME = 20
const PROJECTILE_FLIGHT_MS_FRAC = 0.72
const PROJECTILE_MIN_IMPACT_MS = 200

function isGroundImpactAnchor(anchor: SpriteAnchor): boolean {
  return anchor.y >= FEET_ANCHOR.y - 0.01
}

/** Launch from the caster's hand with the body extending forward, fly the nose
 *  onto the body target, then play the impact/dissipate frames on the authored
 *  anchor. Ground impacts can pin separately without bending the flight path. */
export async function playProjectileLayer(spec: ProjectileLayerSpec): Promise<void> {
  const { host, sheet: sheetDef, scale, from, durationMs } = spec
  const orientation = spec.orientation ?? ''
  const flipped = orientation.includes('scaleX(-1)')
  const noseAnchor = flipped ? flipAnchor(PROJECTILE_NOSE_ANCHOR) : PROJECTILE_NOSE_ANCHOR
  const launchAnchor = flipped ? flipAnchor(PROJECTILE_ORIGIN_ANCHOR) : PROJECTILE_ORIGIN_ANCHOR
  const finalAnchor = spec.pixelated ? noseAnchor : spec.impactAnchor ?? CENTER_ANCHOR
  const baseSize = { w: sheetDef.frameWidth * scale, h: sheetDef.frameHeight * scale }
  const containAnchors = isGroundImpactAnchor(finalAnchor) ? [finalAnchor] : [finalAnchor, noseAnchor]
  const requestedImpactTo = spec.impactTo ?? spec.to
  const contained = containSpriteInHostForAnchors(
    host,
    spec.pixelated ? spec.to : requestedImpactTo,
    containAnchors,
    baseSize.w,
    baseSize.h,
    {
      grow: spec.pixelated ? 1 : 1.14,
      minScaleBeforeShift: 0.58,
    },
  )
  const fittedScale = scale * contained.scale
  const to = spec.pixelated
    ? contained.point
    : {
        x: spec.to.x + (contained.point.x - requestedImpactTo.x),
        y: spec.to.y + (contained.point.y - requestedImpactTo.y),
      }
  const impactTo = contained.point
  const node = spriteNode(host, sheetDef, {
    scale: fittedScale,
    opacity: spec.opacity,
    filter: spec.filter,
    pixelated: spec.pixelated,
  })
  const size = { w: sheetDef.frameWidth * fittedScale, h: sheetDef.frameHeight * fittedScale }
  const opacity = spec.opacity ?? 1
  spec.onLaunch?.()

  // Pixelated strip projectiles (monster arrows/bolts) have no dissipate frames -
  // they are a solid shape that should just fly and land - so keep the original
  // single-phase fly-and-settle for them.
  if (spec.pixelated) {
    node.style.transformOrigin = `${noseAnchor.x * 100}% ${noseAnchor.y * 100}%`
    const sheetRun = animateSheet(node, sheetDef, durationMs)
    const travel = node.animate(
      [
        { transform: placeAt(from, size, launchAnchor, orientation), opacity: Math.min(0.96, opacity) },
        { transform: placeAt(to, size, noseAnchor, orientation), opacity },
      ],
      { duration: durationMs, easing: 'cubic-bezier(0.2, 0.8, 0.25, 1)', fill: 'forwards' },
    )
    await Promise.all([sheetRun, finishAnimation(travel, durationMs)])
    travel.cancel()
    node.remove()
    return
  }

  const fc = sheetDef.frameCount
  const impactStart = clampFrame(spec.impactStartFrame ?? DEFAULT_PROJECTILE_IMPACT_START_FRAME, 1, fc - 1)
  const flightMs = Math.round(durationMs * PROJECTILE_FLIGHT_MS_FRAC)
  const impactMs = Math.max(PROJECTILE_MIN_IMPACT_MS, durationMs - flightMs)

  const launchTransform = placeAt(from, size, launchAnchor, orientation)
  const noseTransform = placeAt(to, size, noseAnchor, orientation)
  const impactAnchor = spec.impactAnchor ?? CENTER_ANCHOR
  const settleTransform = placeAt(impactTo, size, impactAnchor, orientation)

  // Flight: fly frames 0..impactStart-1 from the hand onto the body target,
  // landing the nose there; if the authored impact is ground-rooted, the final
  // keyframe plants the upcoming burst on the floor without changing the flight
  // trajectory.
  node.style.transformOrigin = '50% 50%'
  node.style.transform = launchTransform
  const flight = node.animate(
    [
      { transform: launchTransform, opacity: Math.min(0.96, opacity) },
      { transform: noseTransform, opacity, offset: 0.82 },
      { transform: settleTransform, opacity },
    ],
    { duration: flightMs, easing: 'cubic-bezier(0.2, 0.8, 0.25, 1)', fill: 'forwards' },
  )
  await Promise.all([animateFrameRange(node, sheetDef, 0, impactStart - 1, flightMs), finishAnimation(flight, flightMs)])
  flight.cancel()
  spec.onImpact?.()

  // Impact: hold on the impact point and play the dissipate frames with a short
  // scale-pop and fade. Pinned at settleTransform so the burst stays put on its
  // authored anchor (body center or ground line) instead of drifting.
  node.style.transformOrigin = `${impactAnchor.x * 100}% ${impactAnchor.y * 100}%`
  node.style.transform = settleTransform
  const impact = node.animate(
    [
      { transform: `${settleTransform} scale(1)`, opacity },
      { transform: `${settleTransform} scale(1.06)`, opacity, offset: 0.42 },
      { transform: `${settleTransform} scale(1.12)`, opacity: 0 },
    ],
    { duration: impactMs, easing: 'cubic-bezier(0.16, 1, 0.3, 1)', fill: 'forwards' },
  )
  await Promise.all([animateFrameRange(node, sheetDef, impactStart, fc - 1, impactMs), finishAnimation(impact, impactMs)])
  impact.cancel()
  node.remove()
}

export type ChargeProjectileLayerSpec = {
  host: HTMLElement
  sheet: SpriteAnimation
  scale: number
  from: { x: number; y: number }
  /** Flight target. */
  to: { x: number; y: number }
  /** Optional impact pin for the dissipate phase. */
  impactTo?: { x: number; y: number }
  durationMs: number
  launchStartFrame?: number
  impactStartFrame?: number
  impactAnchor?: SpriteAnchor
  /** Caster faces left (monster) — mirror the charge onto its left/front hand. */
  flip?: boolean
  opacity?: number
  filter?: string
  pixelated?: boolean
  onCharge?: () => void
  onLaunch?: () => void
  onImpact?: () => void
}

// Fallback charge choreography splits the sheet into gather / travel / impact
// phases. Individual sheets can override these frame boundaries because the
// generated effects do not all share one timing pattern.
const DEFAULT_CHARGE_LAUNCH_START_FRAME = 10
const DEFAULT_CHARGE_IMPACT_START_FRAME = 20

function clampFrame(value: number, min: number, max: number): number {
  if (min > max) return min
  return Math.min(max, Math.max(min, Math.round(value)))
}

function phaseDuration(durationMs: number, frameCount: number, totalFrames: number): number {
  return Math.max(1, Math.round(durationMs * (frameCount / Math.max(1, totalFrames))))
}

/**
 * Charge-and-launch projectile: the spell gathers just past the caster's hand,
 * flies its nose onto the target, then dissipates on impact. Shared by the
 * companion (faces right) and monsters (`flip` faces the charge left), so the
 * two never diverge.
 */
export async function playChargeProjectileLayer(spec: ChargeProjectileLayerSpec): Promise<void> {
  const { host, sheet: sheetDef, scale, from, durationMs } = spec
  const baseSize = { w: sheetDef.frameWidth * scale, h: sheetDef.frameHeight * scale }
  const flip = spec.flip ?? false
  const orientation = flip ? ' scaleX(-1)' : ''
  const noseAnchor = flip ? flipAnchor(PROJECTILE_NOSE_ANCHOR) : PROJECTILE_NOSE_ANCHOR
  const impactAnchor = spec.impactAnchor ?? CENTER_ANCHOR
  const containAnchors = isGroundImpactAnchor(impactAnchor) ? [impactAnchor] : [noseAnchor, impactAnchor]
  const requestedImpactTo = spec.impactTo ?? spec.to
  const contained = containSpriteInHostForAnchors(host, requestedImpactTo, containAnchors, baseSize.w, baseSize.h, {
    grow: 1.14,
    minScaleBeforeShift: 0.58,
  })
  const fittedScale = scale * contained.scale
  const to = {
    x: spec.to.x + (contained.point.x - requestedImpactTo.x),
    y: spec.to.y + (contained.point.y - requestedImpactTo.y),
  }
  const impactTo = contained.point
  const node = spriteNode(host, sheetDef, {
    scale: fittedScale,
    opacity: spec.opacity,
    filter: spec.filter,
    pixelated: spec.pixelated,
  })
  const size = { w: sheetDef.frameWidth * fittedScale, h: sheetDef.frameHeight * fittedScale }
  // `flip` faces the caster left (a monster): the charge mirrors to its left/front
  // hand, the exact opposite of the companion's right-hand charge. The art flip
  // is `scaleX(-1)` about the sprite CENTER (transformOrigin 50%), so it mirrors
  // the picture without shifting where the orb sits — placement stays symmetric.
  const dir = flip ? -1 : 1
  // Orb centre sits one hand-clearance past the hand toward the target, so its
  // near edge just clears the hand instead of overlapping the caster's body.
  const gatherCenter = { x: from.x + dir * size.w * 0.56, y: from.y }
  const placeCenter = (pt: { x: number; y: number }) => placeAt(pt, size, CENTER_ANCHOR, orientation)

  const fc = sheetDef.frameCount
  const launchStart = clampFrame(spec.launchStartFrame ?? DEFAULT_CHARGE_LAUNCH_START_FRAME, 1, fc - 2)
  const impactStart = clampFrame(spec.impactStartFrame ?? DEFAULT_CHARGE_IMPACT_START_FRAME, launchStart + 1, fc - 1)
  const gatherEnd = launchStart - 1
  const travelEnd = impactStart - 1
  const gatherMs = phaseDuration(durationMs, launchStart, fc)
  const travelMs = phaseDuration(durationMs, impactStart - launchStart, fc)
  const dissipateMs = Math.max(180, durationMs - gatherMs - travelMs)

  const chargeTransform = placeCenter(gatherCenter)
  const noseTransform = placeAt(to, size, noseAnchor, orientation)
  const impactTransform = placeAt(impactTo, size, impactAnchor, orientation)
  node.style.transformOrigin = '50% 50%'

  // Gather: pulse up at the hand.
  spec.onCharge?.()
  node.style.transform = chargeTransform
  const gather = node.animate(
    [
      { transform: `${chargeTransform} scale(0.76)`, opacity: 0.2 },
      { transform: `${chargeTransform} scale(1)`, opacity: 1, offset: 0.56 },
      { transform: `${chargeTransform} scale(1.03)`, opacity: 1 },
    ],
    { duration: gatherMs, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
  )
  await Promise.all([animateFrameRange(node, sheetDef, 0, gatherEnd, gatherMs), finishAnimation(gather, gatherMs)])
  gather.cancel()

  // Travel: fly onto the target.
  spec.onLaunch?.()
  const travel = node.animate(
    [
      { transform: chargeTransform, opacity: 1 },
      { transform: noseTransform, opacity: 1, offset: 0.82 },
      { transform: impactTransform, opacity: 1 },
    ],
    { duration: travelMs, easing: 'cubic-bezier(0.18, 0.82, 0.24, 1)', fill: 'forwards' },
  )
  await Promise.all([animateFrameRange(node, sheetDef, gatherEnd + 1, travelEnd, travelMs), finishAnimation(travel, travelMs)])
  travel.cancel()
  spec.onImpact?.()

  // Dissipate: burst on the authored impact anchor.
  node.style.transformOrigin = `${impactAnchor.x * 100}% ${impactAnchor.y * 100}%`
  node.style.transform = impactTransform
  const dissipate = node.animate(
    [
      { transform: `${impactTransform} scale(0.98)`, opacity: 1 },
      { transform: `${impactTransform} scale(1.04)`, opacity: 0.82, offset: 0.46 },
      { transform: `${impactTransform} scale(1.12)`, opacity: 0 },
    ],
    { duration: dissipateMs, easing: 'cubic-bezier(0.16, 1, 0.3, 1)', fill: 'forwards' },
  )
  await Promise.all([animateFrameRange(node, sheetDef, travelEnd + 1, fc - 1, dissipateMs), finishAnimation(dissipate, dissipateMs)])
  dissipate.cancel()
  node.remove()
}

export type TargetLayerSpec = {
  host: HTMLElement
  sheet: SpriteAnimation
  scale: number
  to: { x: number; y: number }
  anchor: SpriteAnchor
  durationMs: number
  opacity?: number
  offsetX?: number
  offsetY?: number
  orientation?: string
}

/** Plant the sheet at `anchor` on the target and play a grow-hold-fade. */
export async function playTargetLayer(spec: TargetLayerSpec): Promise<void> {
  const { host, sheet: sheetDef, scale, to, anchor, durationMs } = spec
  const desiredTarget = { x: to.x + (spec.offsetX ?? 0), y: to.y + (spec.offsetY ?? 0) }
  // Fit-to-stage: a boss-sized effect planted at the edge would be cropped by the
  // stage's overflow:hidden. Prefer shrinking at the target point; when the point
  // itself is off-screen, nudge it into the frame so the full silhouette remains visible.
  const baseW = sheetDef.frameWidth * scale
  const baseH = sheetDef.frameHeight * scale
  const contained = containSpriteInHost(host, desiredTarget, anchor, baseW, baseH, {
    grow: 1.04,
    minScaleBeforeShift: 0.6,
  })
  const target = contained.point
  const fittedScale = scale * contained.scale
  const node = spriteNode(host, sheetDef, { scale: fittedScale, opacity: spec.opacity })
  const size = { w: sheetDef.frameWidth * fittedScale, h: sheetDef.frameHeight * fittedScale }
  const transform = placeAt(target, size, anchor, spec.orientation ?? '')
  const opacity = spec.opacity ?? 1
  node.style.transformOrigin = `${anchor.x * 100}% ${anchor.y * 100}%`
  node.style.transform = transform
  const sheetRun = animateSheet(node, sheetDef, durationMs)
  const fade = node.animate(
    [
      { transform: `${transform} scale(0.98)`, opacity: opacity * 0.9 },
      { transform: `${transform} scale(1)`, opacity, offset: 0.18 },
      { transform: `${transform} scale(1)`, opacity, offset: 0.84 },
      { transform: `${transform} scale(1.02)`, opacity: 0 },
    ],
    { duration: durationMs, easing: 'linear', fill: 'forwards' },
  )
  await Promise.all([sheetRun, finishAnimation(fade, durationMs)])
  fade.cancel()
  node.remove()
}
