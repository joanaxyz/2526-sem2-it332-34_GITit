/// <reference types="node" />

import { existsSync } from 'node:fs'
import path from 'node:path'

import { describe, expect, it } from 'vitest'

import { getStoryWorld, listStoryWorldMonsters, listStoryWorlds, STORY_WORLDS } from '@/shared/story-worlds/registry'
import { COMPANIONS, getCompanion, listCompanions } from '@/shared/cosmetics/companions/registry'
import { spriteSourceForSkill } from '@/shared/battle/effects/effectRegistry'
import { storyPreview } from '@/shared/story-worlds/storyPreviews'

const EXPECTED_PARALLAX_KEYS: Record<string, string[]> = {
  'arcane-spire': [
    'chapter-01-foundation-hall',
    'chapter-02-scriptorium-library',
    'chapter-03-branching-gallery',
    'chapter-04-convergence-chamber',
    'chapter-05-recovery-vault',
    'chapter-06-stash-workshop',
    'chapter-07-remote-relay',
    'chapter-08-guild-signal-apex',
  ],
  'frostbound-citadel': [
    'frost-01-forge-gate',
    'frost-02-frozen-bridge',
    'frost-03-blizzard-courtyard',
    'frost-04-icebound-vault',
    'frost-05-aurora-anvil',
    'frost-06-signal-bastion',
    'frost-07-summit-observatory',
    'frost-08-avalanche-debug-tunnel',
    'frost-09-aurora-release-platform',
  ],
  'neon-backstreets': [
    'skyline-01-transit-hub',
    'skyline-02-archive-highrise',
    'skyline-03-debug-lab',
    'skyline-04-simulation-deck',
    'skyline-05-multi-level-campus',
    'skyline-06-automation-district',
    'skyline-07-security-center',
    'skyline-08-maintenance-core',
    'skyline-09-network-operations-center',
    'skyline-10-migration-transit-ring',
    'skyline-09-data-center-roof',
    'skyline-12-command-research-roof',
  ],
}

const PUBLIC_ROOT = existsSync(path.join(process.cwd(), 'public'))
  ? path.join(process.cwd(), 'public')
  : path.join(process.cwd(), 'frontend', 'public')

function collectRegisteredAssetSources(value: unknown, out: string[] = []): string[] {
  if (!value || typeof value !== 'object') return out
  if ('src' in value && typeof value.src === 'string') out.push(value.src)
  for (const nested of Object.values(value)) collectRegisteredAssetSources(nested, out)
  return out
}

function publicAssetPath(src: string): string {
  return path.join(PUBLIC_ROOT, ...src.split('/').filter(Boolean))
}

describe('story world and companion registries', () => {
  it('registers every authored companion slug', () => {
    expect(Object.keys(COMPANIONS).sort()).toEqual(['black', 'blue', 'white'])
    expect(listCompanions().map((companion) => companion.id).sort()).toEqual(['black', 'blue', 'white'])
    expect(getCompanion('blue').sprites.idle.src).toBe('/cosmetics/companion/blue/idle.png')
    expect(getCompanion('white').sprites.idle.src).toBe('/cosmetics/companion/white/idle.png')
    expect(getCompanion('black').sprites.idle.src).toBe('/cosmetics/companion/black/idle.png')
  })

  it('only registers render-ready story worlds', () => {
    expect(Object.keys(STORY_WORLDS)).toEqual(['arcane-spire', 'frostbound-citadel', 'neon-backstreets'])
    expect(listStoryWorlds().map((world) => world.slug)).toEqual([
      'arcane-spire',
      'frostbound-citadel',
      'neon-backstreets',
    ])
  })

  it('uses canonical story identities rather than deprecated placeholder registries', () => {
    expect(STORY_WORLDS['frostbound-citadel'].label).toBe('Frostbound Citadel')
    expect(STORY_WORLDS['frostbound-citadel'].tone).toBe('ice')
    expect(STORY_WORLDS['neon-backstreets'].label).toBe('Neon Backstreets')
    expect(STORY_WORLDS['neon-backstreets'].tone).toBe('neon')
    expect(STORY_WORLDS[`obsidian${'-forge'}`]).toBeUndefined()
    expect(STORY_WORLDS[`void${'-athenaeum'}`]).toBeUndefined()
  })

  it('keeps companions separate from story worlds', () => {
    expect(getCompanion('black').sprites.idle.src).toBe('/cosmetics/companion/black/idle.png')
    expect(spriteSourceForSkill('push', 'black')).toBe(
      '/cosmetics/companion/black/effects/skill-lightning-25/push.png',
    )

    expect(STORY_WORLDS.black).toBeUndefined()
    expect(getStoryWorld('black').slug).toBe('arcane-spire')
  })

  it('falls back to the default story world for an unregistered slug', () => {
    expect(getStoryWorld(undefined).slug).toBe('arcane-spire')
    expect(getStoryWorld('nonexistent-world').slug).toBe('arcane-spire')
  })

  it('resolves every authored chapter parallax to its story-local PNG path', () => {
    for (const [worldSlug, keys] of Object.entries(EXPECTED_PARALLAX_KEYS)) {
      const parallax = STORY_WORLDS[worldSlug]?.battle.parallax ?? {}

      expect(Object.keys(parallax)).toEqual(keys)

      for (const [index, key] of keys.entries()) {
        const src = parallax[key]?.src

        const filename = `chapter-${String(index + 1).padStart(2, '0')}.png`

        expect(src).toBe(`/cosmetics/story-worlds/${worldSlug}/backgrounds/battle/${filename}`)
      }
    }
  })

  it('keeps every registered story asset backed by a shipped public file', () => {
    for (const world of listStoryWorlds()) {
      const sources = [...new Set(collectRegisteredAssetSources(world))]

      expect(sources.length, world.slug).toBeGreaterThan(0)

      for (const src of sources) {
        expect(src, `${world.slug} uses a public asset URL`).toMatch(/^\//)
        expect(existsSync(publicAssetPath(src)), `${world.slug} missing ${src}`).toBe(true)
      }
    }
  })

  it('exposes complete previews for every store-ready story world', () => {
    for (const world of listStoryWorlds()) {
      const preview = storyPreview(world.slug)

      expect(preview, world.slug).toBeDefined()
      expect(preview?.storyMap, world.slug).toBe(world.map?.background.src)
      expect(preview?.battleBackgrounds.length, world.slug).toBeGreaterThan(0)
      expect(preview?.monsterPoses.length, world.slug).toBeGreaterThan(0)
    }
  })

  it('keeps monster fallback foot offsets close enough to the authored ground line', () => {
    for (const world of listStoryWorlds()) {
      for (const [slug, skin] of Object.entries(world.battle.monsters)) {
        const footOffset = skin.metrics.foot_offset
        const frameHeight = skin.sprites.idle?.frameHeight ?? 256

        expect(typeof footOffset, `${world.slug}/${slug}`).toBe('number')
        expect(footOffset, `${world.slug}/${slug}`).toBeGreaterThanOrEqual(0)
        expect(footOffset, `${world.slug}/${slug}`).toBeLessThanOrEqual(Math.floor(frameHeight * 0.36))
      }
    }
  })

  it('exposes the full story world monster registry for shop previews', () => {
    const monsters = listStoryWorldMonsters('arcane-spire')

    expect(monsters).toHaveLength(Object.keys(STORY_WORLDS['arcane-spire'].battle.monsters).length)
    expect(monsters.map((monster) => monster.slug)).toContain('lich-king')
    expect(monsters.map((monster) => monster.slug)).toContain('two-headed-hound')
    expect(monsters.every((monster) => monster.skin === STORY_WORLDS['arcane-spire'].battle.monsters[monster.slug])).toBe(true)
    expect(monsters.every((monster) => !('tier' in monster) && !('tier' in monster.skin))).toBe(true)
  })
})
