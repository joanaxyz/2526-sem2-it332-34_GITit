import { PracticeBriefCard } from '@/shared/practice/components/PracticeContextPanel'
import { normalizePracticeContext } from '@/shared/practice/utils/practiceContext'
import { Badge } from '@/shared/components/Badge'
import type { AdventureAttempt, AdventureRun } from '@/features/command-adventures/types'

/**
 * Scenario brief for an adventure quest. Reuses the challenge workspace's
 * {@link PracticeBriefCard}, passing the attempt's live objective checklist —
 * the objective scaffold is adventure-only.
 */
export function AdventureContextPanel({
  run,
  attempt,
}: {
  run: AdventureRun
  attempt: AdventureAttempt
}) {
  const context = normalizePracticeContext(attempt.scenario_context)

  return (
    <PracticeBriefCard
      title={attempt.quest.title}
      context={context}
      checks={attempt.objective_checks}
      badges={
        <>
          <Badge variant="blue">Adventure</Badge>
          <Badge variant="default">
            Quest {attempt.order + 1} / {run.total_quests}
          </Badge>
          {attempt.quest.is_required ? null : <Badge variant="warning">Optional</Badge>}
        </>
      }
    />
  )
}
