import type { MonsterRuntimeAttackEffect, MonsterRuntimeEffectLayer } from '@/shared/battle/monsterDescriptors'

import type { MonsterBattleEffect, MonsterEffectContext } from './types'
import { playChargeProjectileLayer, playProjectileLayer, playTargetLayer } from './layerPlayback'
import { CENTER_ANCHOR, FEET_ANCHOR, reduceMotion } from './spriteDom'

function orientationTransform(
  orientTo: MonsterRuntimeEffectLayer['orientTo'],
  ctx: MonsterEffectContext,
): string {
  if (orientTo === 'travel') return ctx.to.x < ctx.from.x ? ' scaleX(-1)' : ''
  if (orientTo === 'target-facing' && ctx.targetFacing === 'left') return ' scaleX(-1)'
  return ''
}

function monsterLayer(ctx: MonsterEffectContext, layer: MonsterRuntimeEffectLayer): HTMLElement {
  return layer.layer === 'back' ? ctx.backLayer ?? ctx.layer : ctx.layer
}

/** Monster attacks reuse the same projectile/target playback as companion
 *  skills - one shared core per depth layer - so the two never diverge. */
export function monsterAttackEffect(effect: MonsterRuntimeAttackEffect): MonsterBattleEffect {
  return async (ctx) => {
    if (reduceMotion()) return
    const sizeScale = ctx.sizeScale && ctx.sizeScale > 0 ? ctx.sizeScale : 1
    if (effect.playback === 'projectile') {
      const charge = effect.motion === 'charge'
      const impactAnchor = effect.placeAnchor ?? (effect.anchor === 'feet' ? FEET_ANCHOR : CENTER_ANCHOR)
      const flip = ctx.to.x < ctx.from.x
      await Promise.all(
        effect.layers.map((layer) => {
          const from = { x: ctx.from.x + layer.offsetX, y: ctx.from.y + layer.offsetY }
          const to = { x: ctx.to.x + layer.offsetX, y: ctx.to.y + layer.offsetY }
          const impactTo = ctx.impactTo
            ? { x: ctx.impactTo.x + layer.offsetX, y: ctx.impactTo.y + layer.offsetY }
            : undefined
          const host = monsterLayer(ctx, layer)
          if (charge) {
            return playChargeProjectileLayer({
              host,
              sheet: layer.sheet,
              scale: layer.scale,
              from,
              to,
              impactTo,
              durationMs: effect.durationMs,
              launchStartFrame: effect.launchStartFrame,
              impactStartFrame: effect.impactStartFrame,
              impactAnchor,
              impactScale: sizeScale,
              impactBounds: effect.placeBounds,
              opacity: layer.opacity,
              flip,
            })
          }
          return playProjectileLayer({
            host,
            sheet: layer.sheet,
            scale: layer.scale,
            from,
            to,
            impactTo,
            durationMs: effect.durationMs,
            impactStartFrame: effect.impactStartFrame,
            impactAnchor,
            impactScale: sizeScale,
            impactBounds: effect.placeBounds,
            opacity: layer.opacity,
            orientation: orientationTransform(layer.orientTo, ctx),
          })
        }),
      )
      return
    }
    const anchor = effect.placeAnchor ?? (effect.anchor === 'feet' ? FEET_ANCHOR : CENTER_ANCHOR)
    await Promise.all(
      effect.layers.map((layer) =>
        playTargetLayer({
          host: monsterLayer(ctx, layer),
          sheet: layer.sheet,
          scale: layer.scale * sizeScale,
          to: ctx.to,
          anchor,
          durationMs: effect.durationMs,
          opacity: layer.opacity,
          offsetX: layer.offsetX,
          offsetY: layer.offsetY,
          orientation: orientationTransform(layer.orientTo, ctx),
          visualBounds: effect.placeBounds,
        }),
      ),
    )
  }
}
