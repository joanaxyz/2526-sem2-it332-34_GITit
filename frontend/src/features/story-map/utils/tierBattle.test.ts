import { describe, expect, it } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierRunAssetManifest } from '@/features/story-map/utils/tierBattle'
import { effectSheetForSkill } from '@/shared/battle/effects/effectRegistry'

const run = {
  id: 71,
  tier: { id: 8, adventure_level_id: 13 },
  variant: { id: 4 },
  story: { slug: 'arcane-spire', world_slug: 'arcane-spire' },
  counts: { maximum_counted_commands: 5, remaining_counted_commands: 5 },
  tutor: { command_form: { usage_form: 'git commit -m <message>' } },
  steps: [],
} as unknown as TierRun

describe('tierRunAssetManifest', () => {
  it('preloads the effect of the form the command guide teaches', () => {
    const manifest = tierRunAssetManifest(run, 'blue')
    const sources = [...manifest.images, ...manifest.anchored.map((sheet) => sheet.src)]

    expect(sources).toContain(effectSheetForSkill('commit', 'blue').src)
  })
})
