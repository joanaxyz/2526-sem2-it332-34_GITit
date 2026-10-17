import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { LevelStoryCard } from '@/shared/level/components/LevelContextPanel'
import { hasLevelContext, normalizeLevelContext } from '@/shared/level/utils/levelContext'

/** Scenario and objective for a tier run. The run facts live in TierStatsBar. */
export function TierContextPanel({ run }: { run: TierRun }) {
  const context = contextForRun(run)

  return (
    <LevelStoryCard
      title={run.tier.adventure_level_title}
      context={context}
      labels={{
        story: 'Scenario',
        task: 'Objective',
      }}
      showHeader={false}
      tourTarget="tier-brief"
    />
  )
}

// Legacy tier content puts the case-specific narrative in the first unlabeled
// detail. Labeled details after it are exact, copyable values the learner must
// be given (for example a clone URL or evaluated commit message).
function contextForRun(run: TierRun) {
  const context = normalizeLevelContext(run.scenario_context)
  const narrativeIndex = context.details.findIndex((detail) => !detail.label)
  const narrative = narrativeIndex >= 0 ? context.details[narrativeIndex].value : ''
  const details = context.details.filter((_, index) => index !== narrativeIndex)
  const fallback = normalizeLevelContext({
    story: '',
    task: '',
  })
  const resolved = hasLevelContext(context) ? context : fallback

  return { ...resolved, story: narrative || resolved.story, details }
}
