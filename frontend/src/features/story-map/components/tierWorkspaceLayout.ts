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
