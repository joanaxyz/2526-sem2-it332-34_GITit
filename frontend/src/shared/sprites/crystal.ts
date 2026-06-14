import { backendUrl } from '@/shared/api/httpClient'
import type { BattleArtifactAssetDescriptor } from '@/shared/assets/types'
import type { SpriteAnimation } from '@/shared/sprites/types'

/**
 * The battle-stage crystal Blue defends — descriptor-driven, seeded into the
 * backend (backend/assets/seed_assets/crystal/) like every other sprite. `idle`
 * floats/pulses on a loop; `defeat` plays once and holds the shattered final
 * frame when the run's mana runs dry. `footOffset` (source px of transparent
 * padding below the base) comes from the descriptor config so the stage can
 * stand it on the ledge line.
 */
export type CrystalSheets = {
  idle: SpriteAnimation
  defeat: SpriteAnimation
  footOffset: number
}

const CRYSTAL_FRAME_SIZE = 256
const DEFAULT_FOOT_OFFSET = 52

export function crystalFromDescriptor(descriptor: BattleArtifactAssetDescriptor): CrystalSheets | null {
  const idle = descriptor.sprites.idle
  const defeat = descriptor.sprites.defeat ?? idle
  if (!idle || !defeat) return null
  const footOffset = Number((descriptor.config as { foot_offset?: unknown } | undefined)?.foot_offset)
  return {
    idle: sheet(`${descriptor.slug}.idle`, idle, true),
    defeat: sheet(`${descriptor.slug}.defeat`, defeat, false),
    footOffset: Number.isFinite(footOffset) && footOffset >= 0 ? footOffset : DEFAULT_FOOT_OFFSET,
  }
}

function sheet(
  name: string,
  sprite: { url: string; frame_width: number; frame_height: number; columns: number; rows: number; frame_count: number; fps: number; loops?: boolean },
  defaultLoop: boolean,
): SpriteAnimation {
  return {
    name,
    src: backendUrl(sprite.url),
    frameWidth: positiveInt(sprite.frame_width, CRYSTAL_FRAME_SIZE),
    frameHeight: positiveInt(sprite.frame_height, CRYSTAL_FRAME_SIZE),
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
