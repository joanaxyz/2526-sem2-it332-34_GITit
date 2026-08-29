import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import { effectForSkill, effectPlacementForSkill } from '@/shared/battle/effects/effectRegistry'
import { preloadSpriteSheet } from '@/shared/battle/effects/skill-effects/spriteDom'
import type { CompanionSkill } from '@/shared/cosmetics/companions/companionSkills'

const TARGET_X = 0.72
const TARGET_BODY_Y = 0.47
const TARGET_FEET_Y = 0.82
const SHOWCASE_TARGET_SCALE = 3

type Point = { x: number; y: number }

function pointInLayer(layer: HTMLElement, xFraction: number, yFraction: number): Point {
  const box = layer.getBoundingClientRect()
  return { x: box.width * xFraction, y: box.height * yFraction }
}

function actorAnchor(layer: HTMLElement, actor: HTMLElement | null, xFraction: number, yFraction: number): Point {
  if (!actor) return pointInLayer(layer, 0.24, 0.56)
  const layerBox = layer.getBoundingClientRect()
  const actorBox = actor.getBoundingClientRect()
  return {
    x: actorBox.left - layerBox.left + actorBox.width * xFraction,
    y: actorBox.top - layerBox.top + actorBox.height * yFraction,
  }
}

export async function playCompanionSkillCast({
  skill,
  companionSlug,
  player,
  layer,
  backLayer,
}: {
  skill: CompanionSkill
  companionSlug: string
  player: PlayerActorHandle
  layer: HTMLElement
  backLayer?: HTMLElement | null
}) {
  await preloadSpriteSheet(skill.animation)

  // Match battle choreography: the whole windup completes before the FX
  // leaves the actor, then the cast-end sheet and effect run together.
  await player.attack()

  const { playback, anchor } = effectPlacementForSkill(skill.family, companionSlug)
  const bodyTarget = pointInLayer(layer, TARGET_X, TARGET_BODY_Y)
  const feetTarget = pointInLayer(layer, TARGET_X, TARGET_FEET_Y)
  const from =
    playback === 'ground'
      ? actorAnchor(layer, player.element(), 0.82, 0.99)
      : actorAnchor(layer, player.element(), 0.98, 0.42)
  const feetPlanted = playback === 'ground' || anchor === 'feet'
  const to = playback === 'projectile' ? bodyTarget : feetPlanted ? feetTarget : bodyTarget
  const impactTo = playback === 'projectile' && anchor === 'feet' ? feetTarget : undefined
  const effect = effectForSkill(skill.family, companionSlug)({
    layer,
    backLayer,
    from,
    to,
    impactTo,
    sizeScale: SHOWCASE_TARGET_SCALE,
  })
  const attackEnd = player.endAttack(false)
  await Promise.all([effect, attackEnd])
}
