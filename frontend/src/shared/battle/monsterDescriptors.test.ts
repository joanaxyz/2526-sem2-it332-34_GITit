import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld, listStoryWorlds, monsterSkin } from '@/shared/story-worlds/registry'
import type { SpriteDef } from '@/shared/cosmetics/types'
import type { MonsterEffectPlayback, MonsterSkin } from '@/shared/story-worlds/types'

const sprite: SpriteDef = {
  src: '/monster.png',
  frameWidth: 100,
  frameHeight: 100,
  columns: 1,
  rows: 1,
  frameCount: 1,
  fps: 1,
  loops: true,
}

function monster(species: string): BattleMonster {
  return { id: 0, species, hp: 1, max_hp: 1, alive: true }
}

function skin(partial: Partial<MonsterSkin>): MonsterSkin {
  return {
    label: 'X',
    scale: 1,
    attack: { kind: 'melee' },
    metrics: {},
    sprites: { idle: sprite, attack: sprite },
    ...partial,
  }
}

type ReadmeExpectation = {
  playback: MonsterEffectPlayback
  anchor: 'center' | 'feet'
  placement: 'target' | 'caster'
  motion?: 'charge'
  launchStartFrame?: number
  impactStartFrame?: number
}

function monsterIdFromLayerSource(src: string | undefined): string | null {
  return src?.match(/\/monsters\/(monster-\d+)\/effects\/skill(?:-back)?\.png/)?.[1] ?? null
}

function expectedFromReadme(desc: string): ReadmeExpectation | 'missing' | null {
  if (desc === 'no skill effect spritesheet') return 'missing'
  if (desc === 'target-ground') return { playback: 'target', anchor: 'feet', placement: 'target' }
  if (desc === 'target-center') return { playback: 'target', anchor: 'center', placement: 'target' }
  if (desc === 'caster-center') return { playback: 'target', anchor: 'center', placement: 'caster' }
  const impact = /impact\((center|ground)\) \(f: (\d+) - \d+\)/.exec(desc)
  if (!impact) return null
  const expected: ReadmeExpectation = {
    playback: 'projectile',
    anchor: impact[1] === 'ground' ? 'feet' : 'center',
    placement: 'target',
    impactStartFrame: Number(impact[2]) - 1,
  }
  const fly = /fly \(f: (\d+) - \d+\)/.exec(desc)
  if (desc.startsWith('charge') && fly) {
    expected.motion = 'charge'
    expected.launchStartFrame = Number(fly[1]) - 1
  }
  return expected
}

describe('definitionForMonster combat range', () => {
  it('places projectile archers farther than close melee monsters', () => {
    const soldier = definitionForMonster(
      monster('bone-soldier'),
      skin({ attack: { kind: 'melee', hit_frame: 3, lunge_px: 48 } }),
    )
    const archer = definitionForMonster(
      monster('bone-archer'),
      skin({
        attack: { kind: 'projectile', hit_frame: 6 },
        sprites: { idle: sprite, attack: sprite, projectile: sprite },
      }),
    )

    expect(archer.metrics.combatRangePx).toBeGreaterThan(soldier.metrics.combatRangePx)
  })

  it('lets authored monster metrics override inferred range', () => {
    const custom = definitionForMonster(
      monster('custom-mage'),
      skin({
        attack: { kind: 'projectile', hit_frame: 4 },
        metrics: { range_px: 420 },
        sprites: { idle: sprite, attack: sprite, projectile: sprite },
      }),
    )

    expect(custom.metrics.combatRangePx).toBe(420)
  })

  it('keeps Bone Demon as a ranged caster with a projectile effect', () => {
    const demon = monster('bone-demon')
    const def = definitionForMonster(demon, monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), demon.species))

    expect(def.metrics.scale).toBeGreaterThan(0.5)
    expect(def.attack.kind).toBe('projectile')
    expect(def.attack.flight).toBeUndefined()
    expect(def.attack.effect?.playback).toBe('projectile')
  })
})

describe('definitionForMonster sprite sheets', () => {
  it('treats catalog death sheets as frame animations', () => {
    const ghost = monster('bone-ghost')
    const def = definitionForMonster(ghost, monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), ghost.species))

    expect(def.sprites.death).toMatchObject({
      frameWidth: 256,
      frameHeight: 256,
      columns: 5,
      rows: 5,
      frameCount: 25,
      loop: false,
    })
  })

  it('uses the story-world registry as the monster source of truth', () => {
    const monsters = getStoryWorld(DEFAULT_STORY_WORLD_SLUG).battle.monsters

    expect(monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), 'cursed-lantern')).not.toBeNull()
    expect(monsters['two-headed-hound']).toBeDefined()
    expect(Object.keys(monsters).every((slug) => !slug.includes('_'))).toBe(true)
  })

  it('defines a unique skill effect for every active monster', () => {
    const monsters = getStoryWorld(DEFAULT_STORY_WORLD_SLUG).battle.monsters

    expect(Object.keys(monsters)).toHaveLength(15)
    for (const [slug, skin] of Object.entries(monsters)) {
      expect(skin.sprites.projectile, `${slug} should not use legacy projectile sprites`).toBeUndefined()
      expect(skin.attack.effect?.layers.length, `${slug} should define effect layers`).toBeGreaterThan(0)
      expect(skin.attack.effect?.layers[0].frameCount).toBe(25)
      expect(skin.attack.effect?.layers[0].columns).toBe(5)
      expect(skin.attack.effect?.layers[0].rows).toBe(5)
      const layerSources = skin.attack.effect?.layers.map((layer) => layer.src) ?? []
      expect(layerSources.every((src) => src.includes('/cosmetics/story-worlds/arcane-spire/monsters/'))).toBe(true)
      expect(layerSources.every((src) => !src.includes('/cosmetics/companion/'))).toBe(true)
    }
  })

  it('keeps story monster runtime effects in sync with the spritesheet audit READMEs', () => {
    for (const world of listStoryWorlds()) {
      const text = readFileSync(`public/cosmetics/story-worlds/${world.slug}/monsters/README.md`, 'utf8')
      const effectsByMonsterId = new Map(
        Object.entries(world.battle.monsters)
          .map(([slug, skin]) => {
            const monsterId = monsterIdFromLayerSource(skin.attack.effect?.layers[0]?.src)
            return monsterId ? [monsterId, { slug, skin }] : null
          })
          .filter((entry): entry is [string, { slug: string; skin: MonsterSkin }] => Boolean(entry)),
      )

      for (const line of text.split(/\r?\n/)) {
        const [rawMonsterId, desc] = line.split(' - ')
        if (!rawMonsterId || !desc) continue
        const expected = expectedFromReadme(desc.trim())
        if (!expected) continue
        const monsterId = rawMonsterId.trim()
        const entry = effectsByMonsterId.get(monsterId)
        if (expected === 'missing') {
          expect(entry, `${world.slug} ${monsterId}`).toBeUndefined()
          continue
        }
        expect(entry, `${world.slug} ${monsterId}`).toBeDefined()
        const def = definitionForMonster(monster(entry!.slug), entry!.skin)
        const effect = def.attack.effect
        expect(effect, `${world.slug} ${monsterId}`).toBeDefined()
        expect(effect?.playback, `${world.slug} ${monsterId}`).toBe(expected.playback)
        expect(effect?.anchor, `${world.slug} ${monsterId}`).toBe(expected.anchor)
        expect(effect?.placement, `${world.slug} ${monsterId}`).toBe(expected.placement)
        expect(effect?.motion, `${world.slug} ${monsterId}`).toBe(expected.motion)
        expect(effect?.launchStartFrame, `${world.slug} ${monsterId}`).toBe(expected.launchStartFrame)
        expect(effect?.impactStartFrame, `${world.slug} ${monsterId}`).toBe(expected.impactStartFrame)
      }
    }
  })

  it('normalizes monster projectile effect scale across story worlds while preserving target effect scale', () => {
    const world = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
    const blacksmith = definitionForMonster(monster('bone-blacksmith'), monsterSkin(world, 'bone-blacksmith'))

    for (const storyWorld of listStoryWorlds()) {
      for (const [slug, skin] of Object.entries(storyWorld.battle.monsters)) {
        const def = definitionForMonster(monster(slug), skin)
        if (def.attack.effect?.playback === 'projectile') {
          expect(def.attack.effect.layers.map((layer) => layer.scale), `${storyWorld.slug} ${slug}`).toEqual(
            def.attack.effect.layers.map(() => 0.6),
          )
        }
      }
    }
    expect(blacksmith.attack.effect?.layers[0]?.scale).toBe(0.82)
  })

  it('carries measured monster effect anchors from story data into runtime descriptors', () => {
    const world = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
    const blacksmith = definitionForMonster(monster('bone-blacksmith'), monsterSkin(world, 'bone-blacksmith'))
    const soldier = definitionForMonster(monster('bone-soldier'), monsterSkin(world, 'bone-soldier'))

    expect(blacksmith.attack.effect?.anchor).toBe('feet')
    expect(blacksmith.attack.effect?.placeAnchor?.y).toBeGreaterThan(0.7)
    expect(soldier.attack.effect?.anchor).toBe('center')
    expect(soldier.attack.effect?.placeAnchor?.y).toBeLessThan(0.65)
  })

  it('supports ranged monster effects without a legacy projectile sheet', () => {
    const necromancer = definitionForMonster(
      monster('bone-necromancer'),
      monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), 'bone-necromancer'),
    )
    const soldier = definitionForMonster(
      monster('bone-soldier'),
      monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), 'bone-soldier'),
    )

    expect(necromancer.attack.kind).toBe('projectile')
    if (necromancer.attack.kind !== 'projectile') throw new Error('Expected projectile attack')
    expect(necromancer.attack.sheet).toBeUndefined()
    expect(necromancer.attack.effect?.playback).toBe('target')
    expect(necromancer.attack.effect?.anchor).toBe('feet')
    expect(necromancer.attack.effect?.placement).toBe('target')
    expect(necromancer.metrics.combatRangePx).toBeGreaterThan(soldier.metrics.combatRangePx)
  })

  it('can place target effects around the attacking monster', () => {
    const lantern = definitionForMonster(
      monster('cursed-lantern'),
      monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), 'cursed-lantern'),
    )

    expect(lantern.attack.effect?.playback).toBe('target')
    expect(lantern.attack.effect?.anchor).toBe('center')
    expect(lantern.attack.effect?.placement).toBe('caster')
  })

  it('matches resized monster sheet frames in the registry', () => {
    const monsters = getStoryWorld(DEFAULT_STORY_WORLD_SLUG).battle.monsters

    expect(monsters['bone-demon'].sprites.idle.frameWidth).toBe(384)
    expect(monsters['bone-demon'].sprites.idle.frameHeight).toBe(384)
    expect(monsters['bone-lancer'].sprites.idle.frameWidth).toBe(512)
    expect(monsters['bone-lancer'].sprites.idle.frameHeight).toBe(512)
  })
})
