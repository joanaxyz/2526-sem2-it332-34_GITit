import { LevelBriefCard } from '@/shared/level/components/LevelContextPanel'
import { normalizeLevelContext } from '@/shared/level/utils/levelContext'
import { Badge } from '@/shared/components/Badge'
import type { AdventureAttempt, AdventureRun } from '@/features/command-adventures/types'

/**
 * Scenario brief for an adventure level. Reuses the challenge workspace's
 * {@link LevelBriefCard}, passing the attempt's live objective checklist —
 * the objective scaffold is adventure-only.
 */
export function AdventureContextPanel({
  run,
  attempt,
}: {
  run: AdventureRun
  attempt: AdventureAttempt
}) {
  const context = normalizeLevelContext(attempt.scenario_context)

  return (
    <LevelBriefCard
      title={attempt.level.title}
      context={context}
      checks={attempt.objective_checks}
      badges={
        <>
          <Badge variant="blue">Adventure</Badge>
          <Badge variant="default">
            Level {attempt.order + 1} / {run.total_levels}
          </Badge>
          {attempt.level.is_required ? null : <Badge variant="warning">Optional</Badge>}
        </>
      }
    />
  )
}
