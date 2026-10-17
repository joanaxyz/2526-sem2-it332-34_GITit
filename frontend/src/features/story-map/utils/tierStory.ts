import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { normalizeLevelContext } from '@/shared/level/utils/levelContext'

type TierStoryContent = {
  title: string
  intro: string
  realWorldContext: string
  task: string
  /** Exact literals the learner must type (clone URL, commit message...). */
  requiredValues: { label: string; value: string }[]
}

/**
 * Split a tier run's scenario context into what the workspace shows.
 *
 * Legacy tier content puts the case-specific narrative in the first unlabeled
 * detail; the generic tier story is the fallback. Every other detail is an
 * exact, copyable value.
 */
export function tierStoryContent(
  run: Pick<TierRun, 'scenario_context' | 'variant' | 'tier'>,
): TierStoryContent {
  const context = normalizeLevelContext(run.scenario_context)
  const narrativeIndex = context.details.findIndex((detail) => !detail.label)
  const narrative = narrativeIndex >= 0 ? context.details[narrativeIndex].value : ''
  let intro = narrative || context.story
  let task = context.task
  // Saved runs keep their original briefing even after the scenario bank is reseeded.
  const startingPointIndex = intro.lastIndexOf('\n\nStarting point:')
  if (startingPointIndex >= 0) {
    const startingPoint = intro.slice(startingPointIndex).trim()
    intro = intro.slice(0, startingPointIndex).trimEnd()
    if (!task.includes(startingPoint)) task = [task, startingPoint].filter(Boolean).join('\n\n')
  }

  return {
    title: run.variant?.label?.trim() || run.tier.adventure_level_title,
    intro,
    realWorldContext: context.realWorldContext,
    task,
    requiredValues: context.details.filter((_, index) => index !== narrativeIndex),
  }
}
