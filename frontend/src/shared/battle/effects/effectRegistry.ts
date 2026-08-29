import type { SpriteAnimation } from '@/shared/sprites/types'

import { effectSpecForSkill, effectsForCompanion } from './skill-effects/catalog'
import {
  monsterAttackEffect,
  playMissEffect,
  playResolvedSkillEffect,
  playSpriteProjectileEffect,
} from './skill-effects/playback'
import type {
  BattleEffect,
  FlameTint,
  SkillEffectAnchor,
  SkillEffectPlayback,
} from './skill-effects/types'

export type {
  BattleEffect,
  EffectContext,
  FlameTint,
  SkillEffectAnchor,
  SkillEffectPlayback,
} from './skill-effects/types'
export { monsterAttackEffect }

/** Resolve the effect for a command family ("commit", "merge", ...). */
export function effectForSkill(skill: string, companionSlug?: string | null): BattleEffect {
  const spec = effectSpecForSkill(skill, companionSlug)
  return (ctx) => playResolvedSkillEffect(ctx, spec)
}

/** Whether a skill sheet flies from the companion or plays centered on the target. */
export function effectPlaybackForSkill(skill: string, companionSlug?: string | null): SkillEffectPlayback {
  return effectSpecForSkill(skill, companionSlug).playback
}

/** Playback + anchor, so the battle director can place flight and impact
 *  points: projectiles fly to the body edge, feet-anchored projectile impacts
 *  pin their dissipate frames to the ground, and centered effects sit on the body. */
export function effectPlacementForSkill(
  skill: string,
  companionSlug?: string | null,
): { playback: SkillEffectPlayback; anchor: SkillEffectAnchor } {
  const spec = effectSpecForSkill(skill, companionSlug)
  const anchor: SkillEffectAnchor =
    spec.playback === 'ground'
      ? 'feet'
      : spec.playback === 'target'
        ? spec.anchor ?? 'feet'
        : spec.playback === 'projectile'
          ? spec.anchor ?? 'center'
          : 'center'
  return { playback: spec.playback, anchor }
}

/** The flame tint a command family attacks with. */
export function tintForSkill(skill: string, companionSlug?: string | null): FlameTint {
  return effectSpecForSkill(skill, companionSlug).tint
}

/** Public for lightweight contract tests and UI previews. */
export function spriteSourceForSkill(skill: string, companionSlug?: string | null): string {
  return effectSpecForSkill(skill, companionSlug).sheet.src
}

/** The full effect sheet for a command family - powers still previews
 *  (skill portraits) and any surface that replays the effect outside battle. */
export function effectSheetForSkill(skill: string, companionSlug?: string | null): SpriteAnimation {
  return effectSpecForSkill(skill, companionSlug).sheet
}

/** Public for lightweight contract tests and UI previews. */
export function spriteDisplayMetricsForSkill(
  skill: string,
  companionSlug?: string | null,
): { width: number; height: number; playback: SkillEffectPlayback } {
  const spec = effectSpecForSkill(skill, companionSlug)
  return {
    width: spec.sheet.frameWidth * spec.scale,
    height: spec.sheet.frameHeight * spec.scale,
    playback: spec.playback,
  }
}

/** Played after a missed attack's spell impacts: the fizzled cast deflects off the
 *  target and the miss sheet settles on the open floor. */
export function missedAttackForCompanion(companionSlug?: string | null): BattleEffect {
  const spec = effectsForCompanion(companionSlug).miss
  return (ctx) => playMissEffect(ctx, spec)
}

export const missedAttack: BattleEffect = missedAttackForCompanion()

/**
 * Sprite-strip projectile for monster arrows/magic. Player skills use the
 * generated companion flame sheets above.
 */
export function spriteProjectile(sheetDef: SpriteAnimation, opts?: { hue?: number; flip?: boolean }): BattleEffect {
  return (ctx) => playSpriteProjectileEffect(ctx, sheetDef, opts)
}
