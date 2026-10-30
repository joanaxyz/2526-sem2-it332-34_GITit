import { queryKeys } from '@/shared/api/queryKeys'
import type { WorkspaceScene } from '@/shared/level/workspace/types'
import { storyPath, storyPathWithQuery } from '@/shared/navigation/routes'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

/** Where a tier run sits, for the shared gameplay workspace. */
export function tierScene(run: Pick<TierRun, 'id' | 'tier'>): WorkspaceScene {
  return {
    title: run.tier.adventure_level_title,
    rootName: run.tier.adventure_level_slug,
    runQueryKey: queryKeys.adventureTierRun(run.id),
    battle: { stageKey: String(run.tier.id), levelKey: String(run.tier.adventure_level_id) },
  }
}

export function mapUrlForRun(run: Pick<TierRun, 'chapter' | 'story'>) {
  const storySlug = run.story?.slug
  return run.chapter
    ? storyPathWithQuery(storySlug, `chapter=${run.chapter.id}`)
    : storyPath(storySlug)
}

/** Every new tier attempt opens through TierStartPage, which holds the loading
 * screen until the run exists and its artwork has decoded. */
export function tierStartUrl(
  tierId: number,
  { replay = false, priorRunId }: { replay?: boolean; priorRunId?: number } = {},
) {
  if (replay) return `/adventure-level-tiers/${tierId}/replay`
  const url = `/adventure-level-tiers/${tierId}/runs`
  return priorRunId === undefined ? url : `${url}?prior_run_id=${priorRunId}`
}

export function tierRetryUrl(runId: number) {
  return `/adventure-tier-runs/${runId}/retry`
}
