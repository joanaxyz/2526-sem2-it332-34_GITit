import { describe, expect, it } from 'vitest'

import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld, monsterSkin } from '@/shared/story-worlds/registry'
import type { SpriteDef } from '@/shared/cosmetics/types'
import type { MonsterSkin } from '@/shared/story-worlds/types'

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

function monster(species: string, tier: MonsterSkin['tier'] = 'mob'): BattleMonster {
  return { id: 0, species, tier, hp: 1, max_hp: 1, alive: true }
}

function skin(partial: Partial<MonsterSkin>): MonsterSkin {
  return {
    label: 'X',
    tier: 'mob',
    scale: 1,
    attack: { kind: 'melee' },
    metrics: {},
    sprites: { idle: sprite, attack: sprite },
    ...partial,
  }
}

describe('definitionForMonster combat range', () => {
  it('places projectile archers farther than close melee mobs', () => {
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
    const demon = monster('bone-demon', 'elite')
    const def = definitionForMonster(demon, monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), demon.species))

    expect(def.metrics.scale).toBeGreaterThan(0.7)
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
    }
  })

  it('supports ranged monster effects without a legacy projectile sheet', () => {
    const necromancer = definitionForMonster(
      monster('bone-necromancer', 'elite'),
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
    expect(necromancer.attack.effect?.anchor).toBe('center')
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
