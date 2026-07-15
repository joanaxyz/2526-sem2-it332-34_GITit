import type { SpriteAnimation } from '@/shared/sprites/types'

import skillIndex from './data/companion-skills.json'

/**
 * A single showcaseable companion spell, resolved to a ready-to-play sheet.
 *
 * The index (`data/companion-skills.json`) is generated from the on-disk spell
 * sheets by `scripts/build_companion_skill_index.mjs`, so it only ever lists
 * skills whose art actually exists — a companion that hasn't had a given git
 * command's sheet generated simply omits it here.
 */
export type CompanionSkill = {
  family: string
  command: string
  tint: string
  playback: 'projectile' | 'target' | 'ground' | 'miss'
  anchor: 'center' | 'feet'
  launchStartFrame?: number
  impactStartFrame?: number
  animation: SpriteAnimation
}

type RawSkill = {
  family: string
  command: string
  tint: string
  playback: string
  anchor?: string
  motion?: string
  launchStartFrame?: number
  impactStartFrame?: number
  layers?: { layer: string; src: string }[]
  sheet: {
    src: string
    frameWidth: number
    frameHeight: number
    columns: number
    rows: number
    frameCount: number
    fps: number
  }
}

const INDEX = skillIndex as unknown as Record<string, RawSkill[]>

function toSkill(raw: RawSkill): CompanionSkill {
  return {
    family: raw.family,
    command: raw.command,
    tint: raw.tint,
    playback: raw.playback as CompanionSkill['playback'],
    anchor: (raw.anchor as CompanionSkill['anchor']) ?? 'center',
    launchStartFrame: raw.launchStartFrame,
    impactStartFrame: raw.impactStartFrame,
    animation: {
      name: `${raw.family}.skill`,
      src: raw.sheet.src,
      frameWidth: raw.sheet.frameWidth,
      frameHeight: raw.sheet.frameHeight,
      columns: raw.sheet.columns,
      rows: raw.sheet.rows,
      frameCount: raw.sheet.frameCount,
      fps: raw.sheet.fps,
      loop: false,
    },
  }
}

/** Every spell a companion can showcase, in git-workflow order. */
export function companionSkills(slug: string | null | undefined): CompanionSkill[] {
  const list = (slug && INDEX[slug]) || []
  return list.map(toSkill)
}

export function hasCompanionSkills(slug: string | null | undefined): boolean {
  return companionSkills(slug).length > 0
}
