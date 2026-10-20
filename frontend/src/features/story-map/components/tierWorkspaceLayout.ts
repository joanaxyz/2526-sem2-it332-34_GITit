import { storyPath, storyPathWithQuery } from '@/shared/navigation/routes'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

export const DAG_ZOOM_KEY = 'tier-workspace:dag-zoom-vertical'

export function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
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
