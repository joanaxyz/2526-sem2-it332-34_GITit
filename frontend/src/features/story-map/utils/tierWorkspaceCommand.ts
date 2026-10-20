import type { QueryClient } from '@tanstack/react-query'

import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { stringList } from '@/features/story-map/components/tierWorkspaceLayout'
import { queryKeys } from '@/shared/api/queryKeys'
import { isExitCommand } from '@/shared/level-runtime/commands'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { battleEventsForSubmittedCommand } from '@/shared/level-runtime/commandBattle'
import {
  confirmsPrediction,
  predictLocalOutcome,
  type CommandSubmissionOutcome,
} from '@/shared/level-runtime/commandOutcome'
import type { LearnedSkill } from '@/shared/skill-learning/useSkillLearnedQueue'

export function createTierWorkspaceCommandHandler({
  runId,
  mutation,
  dagAnimation,
  battleDirector,
  queryClient,
  clearToast,
  evaluateAndNotify,
  setExitConfirmOpen,
  setWorkspaceEditorPath,
  queueOutcomeAnimation,
  onSkillsLearned,
}: {
  runId: number
  mutation: ReturnType<typeof useTierCommandSubmission>
  dagAnimation: TierDagAnimationController
  battleDirector: BattleDirector
  queryClient: QueryClient
  clearToast: () => void
  evaluateAndNotify: (run: TierRun, commandClassification: string) => void
  setExitConfirmOpen: (open: boolean) => void
  setWorkspaceEditorPath: (path: string | null) => void
  queueOutcomeAnimation: (runId: number) => void
  onSkillsLearned: (skills: LearnedSkill[]) => void
}) {
  return (command: string) => {
    if (mutation.isPending) return
    if (isExitCommand(command)) {
      setExitConfirmOpen(true)
      return
    }

    clearToast()
    dagAnimation.onCommandStart()
    battleDirector.onAttackStart()

    const resolveTurn = (outcome: CommandSubmissionOutcome) => {
      dagAnimation.onCommandResolved(outcome)
      battleDirector.onResolve(battleEventsForSubmittedCommand({
        command,
        outcome,
        monsters: battleDirector.currentMonsters(),
        storyWorldSlug: runStorySlug(queryClient, runId),
      }))
    }
    const counts = queryClient.getQueryData<TierRun>(queryKeys.adventureTierRun(runId))?.counts
    let predicted: CommandSubmissionOutcome | null = null

    const execution = mutation.mutate(command, {
      onSuccess: (response) => {
        // A turn already played from the local outcome only replays when the
        // server judged it differently (it is the authority on progress).
        if (!predicted || !confirmsPrediction(predicted, response.command_outcome)) {
          resolveTurn(response.command_outcome)
        }
        onSkillsLearned(response.learned_skills ?? [])
        if (response.run.status === 'completed' || response.run.status === 'failed') {
          queueOutcomeAnimation(response.run.id)
        }

        if (response.command_family === 'mergetool') {
          const snapshot = response.run.repository_state
          const requestedPaths = stringList(snapshot.operation_metadata?.last_mergetool_paths)
          const conflictPaths = snapshot.conflicts ?? []
          const nextPath = requestedPaths.find((path) => conflictPaths.includes(path)) ?? conflictPaths[0]
          if (nextPath) setWorkspaceEditorPath(nextPath)
        }

        if (!response.run.replay) {
          const updatedRun = queryClient.getQueryData<TierRun>(queryKeys.adventureTierRun(runId))
          if (updatedRun) {
            evaluateAndNotify(updatedRun, response.step.command_classification)
          }
        }
      },
      onError: () => {
        dagAnimation.onCommandError()
        battleDirector.onError()
      },
    })
    // Misses and read-only looks need no server verdict, so their turn plays
    // now instead of after the round trip.
    predicted = execution && counts
      ? predictLocalOutcome(execution, {
          counted: counts.counted_action_total,
          max: counts.maximum_counted_commands,
        })
      : null
    if (predicted) resolveTurn(predicted)
  }
}

function runStorySlug(queryClient: QueryClient, runId: number) {
  const run = queryClient.getQueryData<TierRun>(queryKeys.adventureTierRun(runId))
  return run?.story?.world_slug ?? run?.story?.slug
}
