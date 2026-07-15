import type { CompanionDef, SpriteDef } from '@/shared/cosmetics/types'
import type { CompanionSpriteDefinition, MoveName, SpriteAnimation } from '@/shared/sprites/types'

/**
 * Battle-only sheets for a companion, kept out of `CompanionSpriteDefinition` so the
 * sprite controller's MoveName contract stays untouched.
 *
 * The battle vocabulary is deliberately small: a companion rests on world idle,
 * plays `attack` when a command fires, `hurt` when struck, and `death` when the
 * run fails. Companion and monster data now share the same combat verb: `attack`.
 */
export type CompanionBattleSheets = {
  attack: SpriteAnimation
  attackEnd: SpriteAnimation
  miss: SpriteAnimation
  hurt: SpriteAnimation
  death: SpriteAnimation
}

const COMPANION_MOVES: MoveName[] = ['idle', 'run']

function animation(sprite: SpriteDef, name: string, opts?: { loop?: boolean; normalizeTo?: SpriteDef }): SpriteAnimation {
  // Sheets ship at heterogeneous resolutions; normalizing to the idle frame
  // keeps one on-screen size.
  const normalizeTo = opts?.normalizeTo
  const displayScale = normalizeTo ? normalizeTo.frameWidth / sprite.frameWidth : 1
  return {
    name,
    src: sprite.src,
    frameWidth: sprite.frameWidth,
    frameHeight: sprite.frameHeight,
    columns: sprite.columns,
    rows: sprite.rows,
    frameCount: sprite.frameCount,
    fps: sprite.fps,
    loop: opts?.loop ?? sprite.loops,
    displayScale,
  }
}

function num(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function optionalNum(value: unknown): number | undefined {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined
}

export function companionFromDef(def: CompanionDef): CompanionSpriteDefinition | null {
  const idle = def.sprites.idle
  if (!idle) return null

  const sprites = Object.fromEntries(
    COMPANION_MOVES.map((move) => {
      const sprite = def.sprites[move] ?? idle
      return [move, animation(sprite, `${def.id}.${move}`, { normalizeTo: idle })]
    }),
  ) as Record<MoveName, SpriteAnimation>

  const randoms = def.randomActions.flatMap((action) => {
    const sprite = def.sprites[action]
    return sprite ? [animation(sprite, `${def.id}.${action}`, { loop: false, normalizeTo: idle })] : []
  })
  const m = def.metrics

  return {
    id: def.id,
    sprites,
    randoms,
    metrics: {
      scale: num(def.scale, 0.65),
      walkSpeed: num(m.walk_speed, 140),
      runSpeed: num(m.run_speed, 280),
      footOffset: num(m.foot_offset, 51),
      teleportDistance: optionalNum(m.teleport_distance),
    },
  }
}

/** Order the shop preview offers animation toggles in, when present. */
const PREVIEW_MOVES = ['idle', 'run', 'attack', 'hurt', 'death'] as const

/**
 * Every sprite sheet a companion has, normalized to one on-screen size, for
 * the shop's preview panel. Unlike `companionFromDef`, this doesn't require
 * `run` to exist and returns whichever sheets are actually authored (a
 * single-pose companion like White/Black just has one entry).
 */
export function companionPreviewAnimations(def: CompanionDef): Record<string, SpriteAnimation> {
  const idle = def.sprites.idle
  if (!idle) return {}
  const entries = PREVIEW_MOVES.flatMap((move) => {
    const sprite = def.sprites[move]
    if (!sprite) return []
    return [[move, animation(sprite, `${def.id}.${move}`, { loop: move === 'idle' || move === 'run', normalizeTo: idle })] as const]
  })
  return Object.fromEntries(entries)
}

export function companionBattleFromDef(def: CompanionDef): CompanionBattleSheets | null {
  const idle = def.sprites.idle
  if (!idle) return null
  const attack = def.sprites.attack ?? idle
  const attackEnd = def.sprites['attack-end'] ?? attack
  const miss = def.sprites.miss ?? attackEnd
  const hurt = def.sprites.hurt ?? idle
  const death = def.sprites.death ?? idle
  return {
    attack: animation(attack, `${def.id}.attack`, { loop: false, normalizeTo: idle }),
    attackEnd: animation(attackEnd, `${def.id}.attack-end`, { loop: false, normalizeTo: idle }),
    miss: animation(miss, `${def.id}.miss`, { loop: false, normalizeTo: idle }),
    hurt: animation(hurt, `${def.id}.hurt`, { loop: false, normalizeTo: idle }),
    death: animation(death, `${def.id}.death`, { loop: false, normalizeTo: idle }),
  }
}
