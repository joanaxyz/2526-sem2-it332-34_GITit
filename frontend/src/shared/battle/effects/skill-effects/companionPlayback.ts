import type { SpriteAnimation } from '@/shared/sprites/types'
import { playSkillSound } from '@/shared/audio/battleAudio'

import type { EffectContext, SkillSpriteSpec, SpriteAnchor } from './types'
import { playChargeProjectileLayer, playProjectileLayer, playTargetLayer } from './layerPlayback'
import {
  CENTER_ANCHOR,
  FEET_ANCHOR,
  animateSheet,
  containSpriteInHost,
  finishAnimation,
  placeAt,
  reduceMotion,
  spriteNode,
} from './spriteDom'

/** The point on the sprite to pin at the target while it rests/impacts. The
 *  pixel-measured `placeAnchor` (emitted from the baked art) wins; otherwise we
 *  fall back to the fixed feet/center frame fraction. */
function impactAnchorFor(spec: SkillSpriteSpec): SpriteAnchor {
  return spec.placeAnchor ?? (spec.anchor === 'feet' ? FEET_ANCHOR : CENTER_ANCHOR)
}

async function playProjectile(
  ctx: EffectContext,
  spec: SkillSpriteSpec,
  options?: {
    opacity?: number
    filter?: string
    flip?: boolean
    pixelated?: boolean
    to?: { x: number; y: number }
    impactScale?: number
  },
): Promise<void> {
  await playProjectileLayer({
    host: ctx.layer,
    sheet: spec.sheet,
    scale: spec.scale,
    from: ctx.from,
    to: options?.to ?? ctx.to,
    impactTo: ctx.impactTo ?? options?.to ?? ctx.to,
    durationMs: spec.durationMs,
    impactAnchor: impactAnchorFor(spec),
    impactScale: options?.impactScale,
    impactBounds: spec.placeBounds,
    impactStartFrame: spec.impactStartFrame,
    opacity: options?.opacity,
    filter: options?.filter,
    pixelated: options?.pixelated,
    orientation: options?.flip ? ' scaleX(-1)' : '',
    onLaunch: spec.element ? () => playSkillSound(spec.element, 'projectile') : undefined,
    onImpact: spec.element ? () => playSkillSound(spec.element, 'impact') : undefined,
  })
}

async function playGatherOrbProjectileImpact(
  ctx: EffectContext,
  spec: SkillSpriteSpec,
  impactScale = 1,
): Promise<void> {
  // The companion faces right, so its charge gathers to the right of the hand.
  // Monsters share this same core with `flip` to mirror it onto their left hand.
  await playChargeProjectileLayer({
    host: ctx.layer,
    sheet: spec.sheet,
    scale: spec.scale,
    from: ctx.from,
    to: ctx.to,
    impactTo: ctx.impactTo ?? ctx.to,
    durationMs: spec.durationMs,
    launchStartFrame: spec.launchStartFrame,
    impactStartFrame: spec.impactStartFrame,
    impactAnchor: impactAnchorFor(spec),
    impactScale,
    impactBounds: spec.placeBounds,
    onCharge: spec.element ? () => playSkillSound(spec.element, 'charge') : undefined,
    onLaunch: spec.element ? () => playSkillSound(spec.element, 'projectile') : undefined,
    onImpact: spec.element ? () => playSkillSound(spec.element, 'impact') : undefined,
  })
}

/** Resolve the runtime placement anchor a target/ground spec was baked for.
 *  Ground effects and feet-anchored risers plant on the ground line; body-centered
 *  target auras were baked to the cell centre and plant on the monster's body. */
function anchorForSpec(spec: SkillSpriteSpec): SpriteAnchor {
  // Pixel-measured anchor wins over the baked-classification fallback.
  if (spec.placeAnchor) return spec.placeAnchor
  if (spec.playback === 'ground') return FEET_ANCHOR
  if (spec.playback === 'target') return spec.anchor === 'center' ? CENTER_ANCHOR : FEET_ANCHOR
  return CENTER_ANCHOR
}

async function playTarget(
  ctx: EffectContext,
  spec: SkillSpriteSpec,
  anchorOverride?: SpriteAnchor,
  frameRange?: { from: number; to: number },
): Promise<void> {
  const anchor = anchorOverride ?? anchorForSpec(spec)
  const layers = spec.layers
  if (layers) {
    // Depth-split: back sheet behind the actors, front sheet in front.
    await Promise.all([
      playTargetLayer({
        host: ctx.backLayer ?? ctx.layer,
        sheet: layers.back,
        scale: spec.scale,
        to: ctx.to,
        anchor,
        durationMs: spec.durationMs,
        offsetX: spec.offsetX,
        offsetY: spec.offsetY,
        frameRange,
        visualBounds: spec.placeBounds,
      }),
      playTargetLayer({
        host: ctx.layer,
        sheet: layers.front,
        scale: spec.scale,
        to: ctx.to,
        anchor,
        durationMs: spec.durationMs,
        offsetX: spec.offsetX,
        offsetY: spec.offsetY,
        frameRange,
        visualBounds: spec.placeBounds,
      }),
    ])
    return
  }
  await playTargetLayer({
    host: ctx.layer,
    sheet: spec.sheet,
    scale: spec.scale,
    to: ctx.to,
    anchor,
    durationMs: spec.durationMs,
    offsetX: spec.offsetX,
    offsetY: spec.offsetY,
    frameRange,
    visualBounds: spec.placeBounds,
  })
}

/** Ground shockwave / cresting wave: base planted on the floor, travelling along
 *  it from the caster's ground point to the enemy's. */
async function playGround(ctx: EffectContext, spec: SkillSpriteSpec): Promise<void> {
  const anchor = spec.placeAnchor ?? FEET_ANCHOR
  // Fit-to-stage against the enemy-side impact point so the shockwave never
  // spills past the clipped stage edge as it comes to rest.
  const baseW = spec.sheet.frameWidth * spec.scale
  const baseH = spec.sheet.frameHeight * spec.scale
  const contained = containSpriteInHost(ctx.layer, ctx.to, anchor, baseW, baseH, {
    grow: 1.03,
    minScaleBeforeShift: 0.62,
  })
  const fittedScale = spec.scale * contained.scale
  const to = contained.point
  const node = spriteNode(ctx.layer, spec.sheet, { scale: fittedScale })
  const w = spec.sheet.frameWidth * fittedScale
  const h = spec.sheet.frameHeight * fittedScale
  const size = { w, h }
  node.style.transformOrigin = `${anchor.x * 100}% ${anchor.y * 100}%`
  const fromTransform = placeAt(ctx.from, size, anchor)
  const impactTransform = placeAt(to, size, anchor)
  const duration = spec.durationMs
  playSkillSound(spec.element, 'ground-run')
  window.setTimeout(() => playSkillSound(spec.element, 'target-ground'), Math.round(duration * 0.72))
  const sheetRun = animateSheet(node, spec.sheet, duration)
  const travel = node.animate(
    [
      { transform: fromTransform, opacity: 0.85 },
      { transform: impactTransform, opacity: 1, offset: 0.72 },
      { transform: impactTransform, opacity: 1 },
    ],
    { duration, easing: 'cubic-bezier(0.22, 0.7, 0.3, 1)', fill: 'forwards' },
  )
  await Promise.all([sheetRun, finishAnimation(travel, duration)])
  travel.cancel()
  node.remove()
}

export async function playResolvedSkillEffect(ctx: EffectContext, spec: SkillSpriteSpec): Promise<void> {
  if (reduceMotion()) return
  // Impacts and target effects follow the rendered monster size.
  const sizeScale = ctx.sizeScale && ctx.sizeScale > 0 ? ctx.sizeScale : 1
  if (spec.motion === 'gather-orb-projectile-impact-dissipate') {
    await playGatherOrbProjectileImpact(ctx, spec, sizeScale)
    return
  }
  if (spec.playback === 'projectile') {
    await playProjectile(ctx, spec, { impactScale: sizeScale })
    return
  }
  const sized = sizeScale === 1 ? spec : { ...spec, scale: spec.scale * sizeScale }
  if (sized.playback === 'ground') {
    await playGround(ctx, sized)
    return
  }
  playSkillSound(sized.element, sized.anchor === 'center' ? 'target-center' : 'target-ground')
  await playTarget(ctx, sized)
}

export async function playSpriteProjectileEffect(
  ctx: EffectContext,
  sheetDef: SpriteAnimation,
  opts?: { hue?: number; flip?: boolean },
): Promise<void> {
  const spec: SkillSpriteSpec = {
    sheet: sheetDef,
    playback: 'projectile',
    tint: 'steel',
    scale: 0.68,
    durationMs: 360,
  }
  const filter = opts?.hue ? `hue-rotate(${opts.hue}deg)` : undefined
  await playProjectile(ctx, spec, { filter, flip: opts?.flip, pixelated: true })
}
