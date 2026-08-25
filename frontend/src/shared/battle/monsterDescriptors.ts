import type { SpriteDef } from '@/shared/cosmetics/types'
import type {
  MonsterAttackEffect,
  MonsterEffectAnchor,
  MonsterEffectLayerDepth,
  MonsterEffectMotion,
  MonsterEffectOrientation,
  MonsterEffectPlacement,
  MonsterEffectPlayback,
  MonsterSkin,
} from '@/shared/story-worlds/types'
import type { BattleMonster } from '@/shared/battle/types'
import type { SpriteAnimation } from '@/shared/sprites/types'
import type { SpriteAnchor, SpriteBounds } from '@/shared/battle/effects/skill-effects/types'

type MonsterAnimName = 'idle' | 'walk' | 'attack' | 'hurt' | 'death'

type MonsterRuntimeAttackFlight = {
  distancePx: number
  liftPx: number
}

type MonsterRuntimeAttackShared = {
  effect?: MonsterRuntimeAttackEffect
  flight?: MonsterRuntimeAttackFlight
}

export type MonsterRuntimeDefinition = {
  id: string
  label: string
  sprites: Record<MonsterAnimName, SpriteAnimation>
  portrait?: string
  attack:
    | ({
        kind: 'melee'
        lungePx: number
        hitFrame: number
      } & MonsterRuntimeAttackShared)
    | ({
        kind: 'projectile'
        sheet?: SpriteAnimation
        launchFrame: number
      } & MonsterRuntimeAttackShared)
  metrics: {
    scale: number
    footOffset: number
    hpBarFraction: number
    combatRangePx: number
  }
}

export type MonsterRuntimeEffectLayer = {
  sheet: SpriteAnimation
  layer: MonsterEffectLayerDepth
  scale: number
  opacity: number
  offsetX: number
  offsetY: number
  orientTo: MonsterEffectOrientation
}

export type MonsterRuntimeAttackEffect = {
  playback: MonsterEffectPlayback
  durationMs: number
  scale: number
  orientTo: MonsterEffectOrientation
  placement: MonsterEffectPlacement
  anchor: MonsterEffectAnchor
  placeAnchor?: SpriteAnchor
  placeBounds?: SpriteBounds
  motion?: MonsterEffectMotion
  launchStartFrame?: number
  impactStartFrame?: number
  layers: MonsterRuntimeEffectLayer[]
}

const FALLBACK_FRAME_SIZE = 100
const MONSTER_PROJECTILE_EFFECT_SCALE = 0.6
const MONSTER_TARGET_EFFECT_SCALE = 0.82
const DEFAULT_LOOP: Record<MonsterAnimName, boolean> = {
  idle: true,
  walk: true,
  attack: false,
  hurt: false,
  death: false,
}

/**
 * Build a monster's runtime visuals from its story-world skin (resolved by the caller
 * via `monsterSkin(storyWorld, species)`, with default-world fallback). The skin
 * supplies art and presentation metrics. No DB, no descriptors.
 */
export function definitionForMonster(
  monster: BattleMonster,
  skin: MonsterSkin | null,
): MonsterRuntimeDefinition {
  if (!skin) return placeholderDefinition(monster)

  const fallbackSprite = skin.sprites.idle ?? skin.sprites.portrait ?? Object.values(skin.sprites)[0]
  if (!fallbackSprite) return placeholderDefinition(monster)

  const sprite = (action: MonsterAnimName): SpriteAnimation =>
    animationFromSkin(skin.sprites[action] ?? fallbackSprite, `${monster.species}.${action}`, DEFAULT_LOOP[action])
  const projectile = skin.sprites.projectile
    ? animationFromSkin(skin.sprites.projectile, `${monster.species}.projectile`, true)
    : null
  const attack = skin.attack ?? { kind: 'melee' as const }
  const effect = effectFromSkin(attack.effect, monster.species)
  const flight = flightFromAttack(attack)

  return {
    id: monster.species,
    label: skin.label || labelFromSlug(monster.species),
    sprites: {
      idle: sprite('idle'),
      walk: sprite('walk'),
      attack: sprite('attack'),
      hurt: sprite('hurt'),
      death: sprite('death'),
    },
    portrait: skin.sprites.portrait?.src,
    attack:
      attack.kind === 'projectile' && (projectile || effect)
        ? {
            kind: 'projectile',
            sheet: projectile ?? undefined,
            launchFrame: positiveInt(attack.hit_frame, 1),
            effect,
            flight,
          }
        : {
            kind: 'melee',
            lungePx: positiveNumber(attack.lunge_px, 56),
            hitFrame: positiveInt(attack.hit_frame, 3),
            effect,
            flight,
          },
    metrics: {
      scale: positiveNumber(monster.scale ?? skin.scale, 1),
      footOffset: positiveNumber(skin.metrics?.foot_offset, 40),
      hpBarFraction: positiveNumber(skin.metrics?.hp_bar_fraction, 0.74),
      combatRangePx: positiveNumber(
        skin.metrics?.range_px,
        inferredCombatRange(monster.species, attack.kind),
      ),
    },
  }
}

function flightFromAttack(attack: { flight_px?: unknown; flight_lift_px?: unknown }): MonsterRuntimeAttackFlight | undefined {
  const distancePx = positiveNumber(attack.flight_px, 0)
  if (distancePx <= 0) return undefined
  return {
    distancePx,
    liftPx: positiveNumber(attack.flight_lift_px, 52),
  }
}

function effectFromSkin(
  effect: MonsterAttackEffect | null | undefined,
  species: string,
): MonsterRuntimeAttackEffect | undefined {
  if (!effect || !Array.isArray(effect.layers) || effect.layers.length === 0) return undefined
  const playback = effect.playback === 'target' ? 'target' : 'projectile'
  const defaultScale = positiveNumber(
    effect.scale,
    playback === 'target' ? MONSTER_TARGET_EFFECT_SCALE : MONSTER_PROJECTILE_EFFECT_SCALE,
  )
  const defaultOrientation = normalizeEffectOrientation(effect.orient_to, playback === 'projectile' ? 'travel' : 'target-facing')
  const placement = playback === 'target' ? normalizeEffectPlacement(effect.placement, 'target') : 'target'
  const anchor = normalizeEffectAnchor(effect.anchor, 'center')
  const placeAnchor = normalizeSpriteAnchor(effect.place_anchor ?? effect.placeAnchor)
  const placeBounds = normalizeSpriteBounds(effect.place_bounds ?? effect.placeBounds)

  // 'charge' is only meaningful for projectiles (the gather-orb windup).
  const motion = playback === 'projectile' && effect.motion === 'charge' ? 'charge' : undefined
  const launchStartFrame = playback === 'projectile' ? nonNegativeInt(effect.launch_start_frame) : undefined
  const impactStartFrame = playback === 'projectile' ? nonNegativeInt(effect.impact_start_frame) : undefined

  return {
    playback,
    durationMs: positiveInt(effect.duration_ms, playback === 'target' ? 860 : 560),
    scale: defaultScale,
    orientTo: defaultOrientation,
    placement,
    anchor,
    ...(placeAnchor ? { placeAnchor } : {}),
    ...(placeBounds ? { placeBounds } : {}),
    motion,
    launchStartFrame,
    impactStartFrame,
    layers: effect.layers.map((layer, index) => ({
      sheet: animationFromSkin(layer, `${species}.effect.${index}`, false),
      layer: layer.layer === 'back' ? 'back' : 'front',
      scale: playback === 'projectile' ? defaultScale : positiveNumber(layer.scale, defaultScale),
      opacity: positiveNumber(layer.opacity, 1),
      offsetX: finiteNumber(layer.offset_x, 0),
      offsetY: finiteNumber(layer.offset_y, 0),
      orientTo: normalizeEffectOrientation(layer.orient_to, defaultOrientation),
    })),
  }
}

function normalizeEffectOrientation(
  value: unknown,
  fallback: MonsterEffectOrientation,
): MonsterEffectOrientation {
  return value === 'none' || value === 'travel' || value === 'target-facing' ? value : fallback
}

function normalizeEffectAnchor(value: unknown, fallback: MonsterEffectAnchor): MonsterEffectAnchor {
  return value === 'center' || value === 'feet' ? value : fallback
}

function normalizeEffectPlacement(value: unknown, fallback: MonsterEffectPlacement): MonsterEffectPlacement {
  return value === 'caster' || value === 'target' ? value : fallback
}

function normalizeSpriteAnchor(value: unknown): SpriteAnchor | undefined {
  if (!value || typeof value !== 'object') return undefined
  const candidate = value as { x?: unknown; y?: unknown }
  const x = Number(candidate.x)
  const y = Number(candidate.y)
  if (!Number.isFinite(x) || !Number.isFinite(y)) return undefined
  return {
    x: Math.min(1, Math.max(0, x)),
    y: Math.min(1, Math.max(0, y)),
  }
}

function normalizeSpriteBounds(value: unknown): SpriteBounds | undefined {
  if (!value || typeof value !== 'object') return undefined
  const candidate = value as Partial<Record<keyof SpriteBounds, unknown>>
  const left = Number(candidate.left)
  const top = Number(candidate.top)
  const right = Number(candidate.right)
  const bottom = Number(candidate.bottom)
  if (![left, top, right, bottom].every(Number.isFinite)) return undefined
  const normalized = {
    left: Math.min(1, Math.max(0, left)),
    top: Math.min(1, Math.max(0, top)),
    right: Math.min(1, Math.max(0, right)),
    bottom: Math.min(1, Math.max(0, bottom)),
  }
  return normalized.left < normalized.right && normalized.top < normalized.bottom ? normalized : undefined
}

export function labelForMonster(monster: BattleMonster | null | undefined): string | null {
  if (!monster) return null
  return labelFromSlug(monster.species)
}

function animationFromSkin(sprite: SpriteDef, name: string, defaultLoop: boolean): SpriteAnimation {
  return {
    name,
    src: sprite.src,
    frameWidth: positiveInt(sprite.frameWidth, FALLBACK_FRAME_SIZE),
    frameHeight: positiveInt(sprite.frameHeight, FALLBACK_FRAME_SIZE),
    columns: positiveInt(sprite.columns, 1),
    rows: positiveInt(sprite.rows, 1),
    frameCount: positiveInt(sprite.frameCount, 1),
    fps: positiveInt(sprite.fps, 12),
    loop: sprite.loops ?? defaultLoop,
    displayScale: positiveNumber(sprite.displayScale, 1),
  }
}

function placeholderDefinition(monster: BattleMonster): MonsterRuntimeDefinition {
  const animation = (action: MonsterAnimName): SpriteAnimation =>
    placeholderAnimation(`${monster.species}.${action}`, DEFAULT_LOOP[action])
  return {
    id: monster.species,
    label: labelFromSlug(monster.species),
    sprites: {
      idle: animation('idle'),
      walk: animation('walk'),
      attack: animation('attack'),
      hurt: animation('hurt'),
      death: animation('death'),
    },
    portrait: placeholderAnimation(`${monster.species}.portrait`, true).src,
    attack: { kind: 'melee', lungePx: 48, hitFrame: 1 },
    metrics: {
      scale: positiveNumber(monster.scale, 1),
      footOffset: 12,
      hpBarFraction: 0.68,
      combatRangePx: inferredCombatRange(monster.species, 'melee'),
    },
  }
}

function inferredCombatRange(slug: string, attackKind: unknown): number {
  if (attackKind === 'projectile') {
    return slug.includes('archer') ? 305 : 285
  }
  return 128
}

function placeholderAnimation(name: string, loop: boolean): SpriteAnimation {
  return {
    name,
    src: placeholderSvg(name.split('.')[0] ?? name),
    frameWidth: FALLBACK_FRAME_SIZE,
    frameHeight: FALLBACK_FRAME_SIZE,
    columns: 1,
    rows: 1,
    frameCount: 1,
    fps: 1,
    loop,
  }
}

function placeholderSvg(species: string): string {
  const label = labelFromSlug(species).slice(0, 2).toUpperCase()
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <rect width="100" height="100" rx="18" fill="hsl(215 40% 10%)"/>
    <rect x="14" y="18" width="72" height="64" rx="16" fill="hsl(202 100% 50%)"/>
    <circle cx="38" cy="44" r="6" fill="hsl(195 60% 95%)"/>
    <circle cx="62" cy="44" r="6" fill="hsl(195 60% 95%)"/>
    <text x="50" y="72" text-anchor="middle" font-size="18" fill="hsl(195 60% 95%)">${label}</text>
  </svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

function positiveInt(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback
}

function nonNegativeInt(value: unknown): number | undefined {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed >= 0 ? Math.floor(parsed) : undefined
}

function positiveNumber(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function finiteNumber(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function labelFromSlug(slug: string): string {
  return slug
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}
