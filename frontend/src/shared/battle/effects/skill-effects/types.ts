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
  /** Multiplier on target/impact art from the target monster's rendered size.
   *  Projectile travel stays at its authored scale; only its landing burst uses
   *  this value. Defaults to 1. */
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
type SkillEffectMotion = 'gather-orb-projectile-impact-dissipate'

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
  /** Pixel-measured placement anchor (normalized 0..1 of the frame), emitted by
   *  process_companion_spell_sheets.py from the baked art. When present, the
   *  runtime pins THIS point on the target instead of the fixed FEET/CENTER
   *  fraction — so a reprocess that shifts the art inside its transparent cell
   *  can't float the effect. Falls back to the `anchor` constant when absent. */
  placeAnchor?: SpriteAnchor
  /** Pixel-measured visible bounds for planted/impact frames, normalized to the
   *  frame. Stage fitting uses this instead of the transparent sprite cell. */
  placeBounds?: SpriteBounds
  offsetX?: number
  offsetY?: number
  /** Two depth passes (back drawn behind the actors, front in front). The
   *  processor bakes both from one shared pivot so they stay aligned. */
  layers?: { back: SpriteAnimation; front: SpriteAnimation }
}

export type SpriteAnchor = { x: number; y: number }
export type SpriteBounds = { left: number; top: number; right: number; bottom: number }
