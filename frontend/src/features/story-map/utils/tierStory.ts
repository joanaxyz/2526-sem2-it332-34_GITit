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

  return {
    title: run.variant?.label?.trim() || run.tier.adventure_level_title,
    intro: narrative || context.story,
    realWorldContext: context.realWorldContext,
    task: context.task,
    requiredValues: context.details.filter((_, index) => index !== narrativeIndex),
  }
}
