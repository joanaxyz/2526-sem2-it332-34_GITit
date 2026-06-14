import { backendUrl } from '@/shared/api/httpClient'
import type { AssetSpriteDescriptor, CharacterAssetDescriptor } from '@/shared/assets/types'
import type { CharacterDefinition, MoveName, SpriteAnimation } from '@/shared/sprites/types'

/**
 * Character rendering is descriptor-driven: sprite sheets are seeded into the
 * backend (backend/assets/seed_assets/character/) and served as media, exactly
 * like monsters. The frontend ships no character image files — it builds a
 * `CharacterDefinition` from the API descriptor at runtime.
 *
 * To add a move or a whole character, seed it on the backend — no component
 * changes. Frames are always 256x256.
 */

const CHARACTER_FRAME_SIZE = 256
const CHARACTER_MOVES: MoveName[] = ['idle', 'walk', 'run', 'fly', 'float', 'dive', 'take_off', 'land']
const REQUIRED_CHARACTER_MOVES: Array<'idle' | 'walk' | 'fly'> = ['idle', 'walk', 'fly']

/** Tuning fallbacks for metrics a descriptor omits (Blue's measured values). */
const DEFAULT_CHARACTER_METRICS: CharacterDefinition['metrics'] = {
  scale: 0.65,
  walkSpeed: 140,
  runSpeed: 280,
  flySpeed: 380,
  footOffset: 51,
  takeOffAirborneFrame: 45,
  takeOffLiftSpeed: 55,
  landFallFrame: 32,
}

export function characterFromDescriptor(descriptor: CharacterAssetDescriptor): CharacterDefinition | null {
  const sprites = Object.fromEntries(
    CHARACTER_MOVES.flatMap((moveName) => {
      const sprite = descriptor.sprites[moveName]
      return sprite ? [[moveName, animationFromDescriptor(sprite, `${descriptor.slug}.${moveName}`, true)]] : []
    }),
  ) as Partial<Record<MoveName, SpriteAnimation>>

  const missing = REQUIRED_CHARACTER_MOVES.filter((moveName) => !sprites[moveName])
  if (missing.length > 0) {
    if (import.meta.env.DEV) {
      console.warn(
        `[characters] "${descriptor.slug}" is missing required sprite sheet(s): ${missing.join(', ')}. ` +
          'Run `python manage.py seed_assets` to (re)seed character assets.',
      )
    }
    return null
  }

  const randomActions = descriptor.random_actions?.length
    ? descriptor.random_actions
    : Object.keys(descriptor.sprites).filter((action) => action.startsWith('random')).sort()
  const randoms = randomActions.flatMap((action) => {
    const sprite = descriptor.sprites[action]
    return sprite ? [animationFromDescriptor(sprite, `${descriptor.slug}.${action}`, false)] : []
  })
  const metrics = descriptor.metrics ?? {}

  return {
    id: descriptor.slug,
    sprites: sprites as CharacterDefinition['sprites'],
    randoms,
    metrics: {
      scale: positiveNumber(descriptor.scale, DEFAULT_CHARACTER_METRICS.scale),
      walkSpeed: positiveNumber(metrics.walk_speed, DEFAULT_CHARACTER_METRICS.walkSpeed),
      runSpeed: positiveNumber(metrics.run_speed, DEFAULT_CHARACTER_METRICS.runSpeed ?? 280),
      flySpeed: positiveNumber(metrics.fly_speed, DEFAULT_CHARACTER_METRICS.flySpeed),
      footOffset: positiveNumber(metrics.foot_offset, DEFAULT_CHARACTER_METRICS.footOffset),
      teleportDistance: optionalPositiveNumber(metrics.teleport_distance),
      takeOffAirborneFrame: optionalPositiveNumber(metrics.take_off_airborne_frame),
      takeOffLiftSpeed: optionalPositiveNumber(metrics.take_off_lift_speed),
      landFallFrame: optionalPositiveNumber(metrics.land_fall_frame),
    },
  }
}

/**
 * Battle-only sheets for a character, kept out of `CharacterDefinition` so the
 * tower controller's MoveName contract is untouched. `cast` plays once per
 * spell; `miss` has no dedicated sheet yet, so it reuses the idle frames as a
 * placeholder beat. Returns null until the descriptor has the needed actions.
 */
export type CharacterBattleSheets = { cast: SpriteAnimation; miss: SpriteAnimation }

export function characterBattleFromDescriptor(
  descriptor: CharacterAssetDescriptor,
): CharacterBattleSheets | null {
  const idle = descriptor.sprites.idle
  const cast = descriptor.sprites.cast ?? idle
  if (!idle || !cast) return null
  return {
    cast: animationFromDescriptor(cast, `${descriptor.slug}.cast`, false),
    miss: animationFromDescriptor(idle, `${descriptor.slug}.miss`, false),
  }
}

function animationFromDescriptor(
  sprite: AssetSpriteDescriptor,
  name: string,
  defaultLoop: boolean,
): SpriteAnimation {
  return {
    name,
    src: backendUrl(sprite.url),
    frameWidth: positiveInt(sprite.frame_width, CHARACTER_FRAME_SIZE),
    frameHeight: positiveInt(sprite.frame_height, CHARACTER_FRAME_SIZE),
    columns: positiveInt(sprite.columns, 1),
    rows: positiveInt(sprite.rows, 1),
    frameCount: positiveInt(sprite.frame_count, 1),
    fps: positiveInt(sprite.fps, 12),
    loop: sprite.loops ?? defaultLoop,
  }
}

function positiveInt(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback
}

function positiveNumber(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function optionalPositiveNumber(value: unknown): number | undefined {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined
}
