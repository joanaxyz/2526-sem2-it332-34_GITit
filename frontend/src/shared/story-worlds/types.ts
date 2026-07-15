import type { SpriteDef } from '@/shared/cosmetics/types'

/** Pure-CSS sky: a base color plus a layered gradient stack. */
export type SkyDef = {
  base: string
  background: string
  starfield?: boolean
}

export type MonsterTier = 'mob' | 'elite' | 'boss'

export type MonsterEffectPlayback = 'projectile' | 'target'
export type MonsterEffectLayerDepth = 'front' | 'back'
export type MonsterEffectOrientation = 'none' | 'travel' | 'target-facing'
export type MonsterEffectAnchor = 'center' | 'feet'
export type MonsterEffectPlacement = 'target' | 'caster'
/** Projectile windup style: 'charge' gathers the bolt at the monster's front
 *  (left) hand before firing, mirroring the companion's right-hand charge. */
export type MonsterEffectMotion = 'charge'

export type MonsterEffectLayer = SpriteDef & {
  layer?: MonsterEffectLayerDepth
  scale?: number
  opacity?: number
  offset_x?: number
  offset_y?: number
  orient_to?: MonsterEffectOrientation
}

export type MonsterAttackEffect = {
  playback: MonsterEffectPlayback
  duration_ms?: number
  scale?: number
  orient_to?: MonsterEffectOrientation
  /** Target effects can either hit Blue or wrap the attacking monster. */
  placement?: MonsterEffectPlacement
  /** Target effects default to body-center; feet remains for ground-planted art. */
  anchor?: MonsterEffectAnchor
  /** Projectile-only: 'charge' plays the gather-orb windup on the front hand. */
  motion?: MonsterEffectMotion
  layers: MonsterEffectLayer[]
}

export type MonsterAttack = {
  kind: 'melee' | 'projectile'
  hit_frame?: number
  lunge_px?: number
  flight_px?: number
  flight_lift_px?: number
  projectile?: string
  effect?: MonsterAttackEffect
}

export type MonsterMetrics = {
  foot_offset?: number
  hp_bar_fraction?: number
  range_px?: number
}

/** The visual skin for one catalog monster id. Gameplay HP/tier live backend-side. */
export type MonsterSkin = {
  label: string
  tier: MonsterTier
  scale: number
  attack: MonsterAttack
  metrics: MonsterMetrics
  sprites: Record<string, SpriteDef>
}

/** Battle visuals a story world supplies: backdrop, optional dressing, and monster skins. */
export type StoryBattleDef = {
  backdrop: SpriteDef
  sky?: SpriteDef
  parallax?: Record<string, SpriteDef>
  crystal?: { config: { foot_offset?: number }; sprites: Record<string, SpriteDef> }
  monsters: Record<string, MonsterSkin>
}

export type StoryMapDef = {
  background: SpriteDef
}

export type StoryWorldTone = 'blue' | 'ice' | 'shadow' | 'neon'

/** Semantic CSS tokens a render-ready story world owns. Values are RGB triplets without rgb(). */
export type StoryWorldTokens = {
  primaryRgb: string
  secondaryRgb: string
  accentRgb: string
  surfaceRgb: string
  glowRgb: string
  sparkRgb: string
}

export type StoryWorldPreviewDef = {
  battleBackgrounds?: string[]
  monsterPoses?: string[]
}

export type StoryWorldDef = {
  slug: string
  label: string
  tone: StoryWorldTone
  sky: SkyDef
  tokens: StoryWorldTokens
  battle: StoryBattleDef
  map?: StoryMapDef
  preview?: StoryWorldPreviewDef
}
