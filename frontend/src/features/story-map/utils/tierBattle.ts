import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierScene } from '@/features/story-map/components/tierWorkspaceLayout'
import type { BattleAssetManifest } from '@/shared/battle/battleAssets'
import { workspaceRunAssetManifest } from '@/shared/level/workspace/workspaceBattle'

/** Every image the Tier battle can paint, including the effect of the form a command guide teaches. */
export function tierRunAssetManifest(run: TierRun, companionSlug: string): BattleAssetManifest {
  return workspaceRunAssetManifest(
    run,
    tierScene(run).battle,
    companionSlug,
    run.tutor ? [run.tutor.command_form.usage_form] : [],
  )
}
