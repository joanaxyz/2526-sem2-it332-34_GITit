import type { DrillPlan } from '@/features/drills/types'
import { storyPath, storyPathWithQuery } from '@/shared/navigation/routes'

/**
 * Where leaving the drill goes: the map the learner came from.
 *
 * The payload carries an empty slug for a level with no owning story, in
 * which case `storyPath` falls back to the default story rather than
 * building `/stories/` and 404ing the way out of a practice screen.
 */
export function drillExitPath(plan: DrillPlan): string {
  return storyPath(plan.level.story_slug || undefined)
}

/** The owning level teaches the drill's forms; open its choices on the map. */
export function drillPracticePath(plan: DrillPlan): string {
  const query = new URLSearchParams()
  if (plan.level.chapter_id != null) query.set('chapter', String(plan.level.chapter_id))
  query.set('level', String(plan.level.id))
  return storyPathWithQuery(plan.level.story_slug || undefined, query.toString())
}
