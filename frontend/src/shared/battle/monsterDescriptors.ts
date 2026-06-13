import { backendUrl } from '@/shared/api/httpClient'
import type { BattleMonster, BattleSpriteDescriptor } from '@/shared/battle/types'
import type { SpriteAnimation } from '@/shared/sprites/types'

export type MonsterAnimName = 'idle' | 'walk' | 'attack' | 'hurt' | 'death'

export type MonsterRuntimeDefinition = {
  id: string
  label: string
  tier: 'mob' | 'elite' | 'boss'
  sprites: Record<MonsterAnimName, SpriteAnimation>
  portrait?: string
  attack:
    | {
        kind: 'melee'
        lungePx: number
        hitFrame: number
      }
    | {
        kind: 'projectile'
        sheet: SpriteAnimation
        launchFrame: number
      }
  metrics: {
    scale: number
    footOffset: number
    hpBarFraction: number
  }
}

const FALLBACK_FRAME_SIZE = 100
const DEFAULT_LOOP: Record<MonsterAnimName, boolean> = {
  idle: true,
  walk: true,
  attack: false,
  hurt: false,
  death: false,
}

export function definitionForMonster(monster: BattleMonster): MonsterRuntimeDefinition {
  const descriptor = monster.descriptor
  if (!descriptor) return placeholderDefinition(monster)

  const fallbackSprite =
    descriptor.sprites.idle ??
    descriptor.sprites.portrait ??
    Object.values(descriptor.sprites)[0]

  if (!fallbackSprite) return placeholderDefinition(monster)

  const sprite = (action: MonsterAnimName): SpriteAnimation =>
    animationFromDescriptor(
      descriptor.sprites[action] ?? fallbackSprite,
      `${descriptor.slug}.${action}`,
      DEFAULT_LOOP[action],
    )
  const projectile = descriptor.sprites.projectile
    ? animationFromDescriptor(descriptor.sprites.projectile, `${descriptor.slug}.projectile`, true)
    : null
  const attack = descriptor.attack ?? {}

  return {
    id: descriptor.slug,
    label: descriptor.label || labelFromSlug(monster.species),
    tier: normalizeTier(descriptor.tier ?? monster.tier),
    sprites: {
      idle: sprite('idle'),
      walk: sprite('walk'),
      attack: sprite('attack'),
      hurt: sprite('hurt'),
      death: sprite('death'),
    },
    portrait: descriptor.sprites.portrait ? backendUrl(descriptor.sprites.portrait.url) : undefined,
    attack:
      attack.kind === 'projectile' && projectile
        ? {
            kind: 'projectile',
            sheet: projectile,
            launchFrame: positiveInt(attack.hit_frame, 1),
          }
        : {
            kind: 'melee',
            lungePx: positiveNumber(attack.lunge_px, 56),
            hitFrame: positiveInt(attack.hit_frame, 3),
          },
    metrics: {
      scale: positiveNumber(monster.scale ?? descriptor.scale, 1),
      footOffset: positiveNumber(descriptor.metrics?.foot_offset, 16),
      hpBarFraction: positiveNumber(descriptor.metrics?.hp_bar_fraction, 0.74),
    },
  }
}

export function labelForMonster(monster: BattleMonster | null | undefined): string | null {
  if (!monster) return null
  return monster.descriptor?.label || labelFromSlug(monster.species)
}

export function portraitForMonster(monster: BattleMonster | null | undefined): string | null {
  const portrait = monster?.descriptor?.sprites.portrait
  return portrait ? backendUrl(portrait.url) : null
}

function animationFromDescriptor(
  sprite: BattleSpriteDescriptor,
  name: string,
  defaultLoop: boolean,
): SpriteAnimation {
  return {
    name,
    src: backendUrl(sprite.url),
    frameWidth: positiveInt(sprite.frame_width, FALLBACK_FRAME_SIZE),
    frameHeight: positiveInt(sprite.frame_height, FALLBACK_FRAME_SIZE),
    columns: positiveInt(sprite.columns, 1),
    rows: positiveInt(sprite.rows, 1),
    frameCount: positiveInt(sprite.frame_count, 1),
    fps: positiveInt(sprite.fps, 12),
    loop: sprite.loops ?? defaultLoop,
  }
}

function placeholderDefinition(monster: BattleMonster): MonsterRuntimeDefinition {
  const animation = (action: MonsterAnimName): SpriteAnimation =>
    placeholderAnimation(`${monster.species}.${action}`, DEFAULT_LOOP[action])
  return {
    id: monster.species,
    label: labelFromSlug(monster.species),
    tier: monster.tier,
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
      scale: positiveNumber(monster.scale, monster.tier === 'boss' ? 1.4 : 1),
      footOffset: 12,
      hpBarFraction: 0.68,
    },
  }
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
    <rect width="100" height="100" rx="18" fill="#122433"/>
    <rect x="14" y="18" width="72" height="64" rx="16" fill="#1f7a8c"/>
    <circle cx="38" cy="44" r="6" fill="#f8fafc"/>
    <circle cx="62" cy="44" r="6" fill="#f8fafc"/>
    <text x="50" y="72" text-anchor="middle" font-family="monospace" font-size="18" fill="#f8fafc">${label}</text>
  </svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

function normalizeTier(value: unknown): 'mob' | 'elite' | 'boss' {
  return value === 'elite' || value === 'boss' ? value : 'mob'
}

function positiveInt(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback
}

function positiveNumber(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function labelFromSlug(slug: string): string {
  return slug
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}
