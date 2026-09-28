import { describe, expect, it } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierBattleEncounter, tierRunAssetManifest } from '@/features/story-map/utils/tierBattle'
import { effectSheetForSkill } from '@/shared/battle/effects/effectRegistry'
import { getStoryWorld } from '@/shared/story-worlds/registry'

const run = {
  id: 71,
  tier: { id: 8, adventure_level_id: 13 },
  variant: { id: 4 },
  story: { slug: 'arcane-spire', world_slug: 'arcane-spire' },
  counts: { maximum_counted_commands: 5, remaining_counted_commands: 5 },
  tutor: { command_form: { usage_form: 'git commit -m <message>' } },
  steps: [],
} as unknown as TierRun

describe('tierBattleEncounter', () => {
  it('builds the same deterministic roster used by the visible stage', () => {
    const first = tierBattleEncounter({
      runId: run.id,
      tierId: run.tier.id,
      adventureLevelId: run.tier.adventure_level_id,
      variantId: run.variant.id,
      storySlug: run.story?.slug,
      storyWorldSlug: run.story?.world_slug,
      maxHp: run.counts.maximum_counted_commands,
    })
    const second = tierBattleEncounter({
      runId: run.id,
      tierId: run.tier.id,
      adventureLevelId: run.tier.adventure_level_id,
      variantId: run.variant.id,
      storySlug: run.story?.slug,
      storyWorldSlug: run.story?.world_slug,
      maxHp: run.counts.maximum_counted_commands,
    })

    expect(second.roster).toEqual(first.roster)
    expect(first.roster[0]?.max_hp).toBe(5)
  })
})

describe('tierRunAssetManifest', () => {
  it('includes the stage roster, backdrop, companion and taught command effect', () => {
    const storyWorld = getStoryWorld('arcane-spire')
    const manifest = tierRunAssetManifest(run, 'blue')
    const sources = [...manifest.images, ...manifest.anchored.map((sheet) => sheet.src)]

    expect(sources).toContain(storyWorld.battle.backdrop.src)
    expect(sources).toContain(effectSheetForSkill('commit', 'blue').src)
    expect(sources.some((src) => src.includes('/companion/blue/idle.png'))).toBe(true)
    expect(
      Object.values(storyWorld.battle.monsters).some((monster) =>
        sources.includes(monster.sprites.idle.src),
      ),
    ).toBe(true)
  })
})
