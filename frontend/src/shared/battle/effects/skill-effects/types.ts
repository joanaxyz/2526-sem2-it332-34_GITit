import type { SpriteAnimation } from '@/shared/sprites/types'
import type { BattleSkillElement } from '@/shared/audio/battleAudio'

export type EffectContext = {
  /** Absolutely-positioned overlay (`contain: strict`, pointer-events none). */
  layer: HTMLElement
  /** Optional lower overlay, rendered behind the actors for the back depth pass
   *  of a layered spell (and for monster ground/aura effects). */
  backLayer?: HTMLElement | null
  /** Launch point, layer-local px. */
  from: { x: number; y: number }
  /** Flight target / body impact point, layer-local px. */
  to: { x: number; y: number }
  /** Optional impact pin for projectile dissipate frames. Ground-impact sheets
   *  fly to `to`, then plant their burst here without bending the flight path. */
  impactTo?: { x: number; y: number }
  /** Multiplier on the effect's base scale, from the target monster's size, so
   *  the spell grows with a big boss and shrinks for a small mob. Defaults to 1. */
  sizeScale?: number
}

export type BattleEffect = (ctx: EffectContext) => Promise<void>
export type MonsterEffectContext = EffectContext & {
  /** Direction the hit target is facing; target-centered sheets can mirror to it. */
  targetFacing?: 'left' | 'right'
}
export type MonsterBattleEffect = (ctx: MonsterEffectContext) => Promise<void>
export type SkillEffectPlayback = 'projectile' | 'target' | 'ground' | 'miss'
/** Where a target/ground effect plants: on the enemy body, or on its ground line. */
export type SkillEffectAnchor = 'center' | 'feet'
export type FlameTint = 'cyan' | 'azure' | 'indigo' | 'steel' | 'violet' | 'ash'
export type SkillEffectMotion = 'gather-orb-projectile-impact-dissipate'

export type SkillSpriteSpec = {
  sheet: SpriteAnimation
  playback: SkillEffectPlayback
  tint: FlameTint
  element?: BattleSkillElement
  scale: number
  durationMs: number
  motion?: SkillEffectMotion
  /** For `target` playback: whether the effect plants on the monster's body
   *  ("center", a baked-to-cell-centre aura/burst) or on its ground line
   *  ("feet", a ground-rooted riser). For `projectile`, this optionally controls
   *  where the impact/dissipate frames pin after the flight lands.
   *  Must match the classification in process_companion_spell_sheets.py. */
  anchor?: SkillEffectAnchor
  /** Zero-based first frame that leaves the caster during charge playback. */
  launchStartFrame?: number
  /** Zero-based first frame that should hold on the impact point. */
  impactStartFrame?: number
  offsetX?: number
  offsetY?: number
  /** Two depth passes (back drawn behind the actors, front in front). The
   *  processor bakes both from one shared pivot so they stay aligned. */
  layers?: { back: SpriteAnimation; front: SpriteAnimation }
}

export type SpriteAnchor = { x: number; y: number }
