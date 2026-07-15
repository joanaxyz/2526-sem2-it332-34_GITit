import type { AdventureRun } from '@/features/adventures/types'
import { storyPath, storyPathWithQuery } from '@/shared/navigation/routes'

export function mapUrlForAdventure(run: AdventureRun) {
  const storySlug = run.story?.slug
  return run.chapter_id
    ? storyPathWithQuery(storySlug, `chapter=${run.chapter_id}`)
    : storyPath(storySlug)
}
