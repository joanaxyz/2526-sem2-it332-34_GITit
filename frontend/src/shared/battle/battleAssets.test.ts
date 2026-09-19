import { describe, expect, it } from 'vitest'

import { battleAssetManifest, monsterAssetManifest } from './battleAssets'
import { effectSheetForSkill } from './effects/effectRegistry'
import { getStoryWorld } from '@/shared/story-worlds/registry'

const storyWorld = getStoryWorld('arcane-spire')
const SPECIES = 'bone-archer'

function manifest(overrides: Partial<Parameters<typeof battleAssetManifest>[0]> = {}) {
  return battleAssetManifest({
    storyWorld,
    companionSlug: 'blue',
    species: [SPECIES],
    skillSlugs: ['git-commit'],
    ...overrides,
  })
}

function sources(built: ReturnType<typeof battleAssetManifest>): string[] {
  return [...built.images, ...built.anchored.map((sheet) => sheet.src)]
}

describe('battleAssetManifest', () => {
  it('claims the chapter backdrop the stage names', () => {
    const chapter = manifest({ stage: { parallax: { slug: 'chapter-03-branching-gallery' }, landing: null } })

    expect(chapter.images).toContain(storyWorld.battle.parallax?.['chapter-03-branching-gallery']?.src)
  })

  it('falls back to the story world backdrop when the stage names none', () => {
    expect(manifest().images).toContain(storyWorld.battle.backdrop.src)
  })

  it('anchors the sheets the actors measure themselves against', () => {
    const anchored = manifest().anchored.map((sheet) => sheet.src)

    expect(anchored).toContain(storyWorld.battle.monsters[SPECIES].sprites.idle.src)
    expect(anchored.some((src) => src.includes('/companion/blue/idle.png'))).toBe(true)
    expect(anchored.some((src) => src.includes('/companion/blue/run.png'))).toBe(true)
  })

  it('claims every sheet the companion fights with', () => {
    const images = manifest().images

    for (const pose of ['attack.png', 'attack-end.png', 'miss.png', 'hurt.png', 'death.png']) {
      expect(images.some((src) => src.endsWith(`/companion/blue/${pose}`))).toBe(true)
    }
  })

  it('claims the foe it will stage, down to its attack effect layers', () => {
    const images = manifest().images
    const skin = storyWorld.battle.monsters[SPECIES]

    expect(images).toContain(skin.sprites.attack.src)
    expect(images).toContain(skin.sprites.death.src)
    expect(images).toContain(skin.attack.effect?.layers[0].src)
  })

  it('resolves a curriculum skill slug to the spell sheet it casts', () => {
    expect(manifest().images).toContain(effectSheetForSkill('commit', 'blue').src)
  })

  it('always claims the fallback spell, whatever the level teaches', () => {
    expect(manifest({ skillSlugs: [] }).images).toContain(effectSheetForSkill('default', 'blue').src)
  })

  it('claims each source once when several command forms share a skill', () => {
    const built = manifest({ skillSlugs: ['git-commit', 'git-commit', 'commit'] })
    const all = sources(built)

    expect(all.length).toBe(new Set(all).size)
  })
})

describe('monsterAssetManifest', () => {
  it('claims the foe without the rest of the encounter', () => {
    const built = monsterAssetManifest(storyWorld, [SPECIES])

    expect(built.anchored.map((sheet) => sheet.src)).toEqual([
      storyWorld.battle.monsters[SPECIES].sprites.idle.src,
    ])
    expect(built.images).not.toContain(storyWorld.battle.backdrop.src)
  })
})
