import { describe, expect, it } from 'vitest'

import { effectSheetForSkill } from '@/shared/battle/effects/effectRegistry'
import { workspaceBattleEncounter, workspaceRunAssetManifest } from '@/shared/level/workspace/workspaceBattle'
import { getStoryWorld } from '@/shared/story-worlds/registry'

const run = {
  id: 71,
  variant: { id: 4, label: '' },
  story: { slug: 'arcane-spire', world_slug: 'arcane-spire' },
  counts: { counted_action_total: 0, maximum_counted_commands: 5, remaining_counted_commands: 5 },
  steps: [],
}
const battle = { stageKey: '8', levelKey: '13' }

describe('workspaceBattleEncounter', () => {
  it('builds the same deterministic roster used by the visible stage', () => {
    const input = {
      runId: run.id,
      variantId: run.variant.id,
      battle,
      storySlug: run.story.slug,
      storyWorldSlug: run.story.world_slug,
      maxHp: run.counts.maximum_counted_commands,
    }
    const first = workspaceBattleEncounter(input)
    const second = workspaceBattleEncounter(input)

    expect(second.roster).toEqual(first.roster)
    expect(first.roster[0]?.max_hp).toBe(5)
    expect(first.encounterKey).toBe('71:8:4')
  })
})

describe('workspaceRunAssetManifest', () => {
  it('includes the stage roster, backdrop, companion and the extra command effects', () => {
    const storyWorld = getStoryWorld('arcane-spire')
    const manifest = workspaceRunAssetManifest(run, battle, 'blue', ['git commit -m <message>'])
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
