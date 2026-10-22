import type { QueryClient } from '@tanstack/react-query'

import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import type { ChallengeRun } from '@/features/challenges/types'
import { queryKeys } from '@/shared/api/queryKeys'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { battleEventsForSubmittedCommand } from '@/shared/level-runtime/commandBattle'
import {
  confirmsPrediction,
  predictLocalOutcome,
  type CommandSubmissionOutcome,
} from '@/shared/level-runtime/commandOutcome'
import { isExitCommand, isGitCommand } from '@/shared/level-runtime/commands'
import { stringList } from '@/shared/level/workspace/layout'
import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'

export function createChallengeWorkspaceCommandHandler({
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
}: {
  runId: number
  mutation: ReturnType<typeof useChallengeCommandSubmission>
  dagAnimation: DagAnimationController
  battleDirector: BattleDirector
  queryClient: QueryClient
  clearToast: () => void
  evaluateAndNotify: (run: ChallengeRun, commandClassification: string) => void
  setExitConfirmOpen: (open: boolean) => void
  setWorkspaceEditorPath: (path: string | null) => void
  queueOutcomeAnimation: (runId: number) => void
}) {
  return (command: string) => {
    // Drop a command fired while the previous one is still in flight (fast
    // double-tap / Enter race): two for the same run collide on the row lock
    // server-side and would be rejected anyway.
    if (mutation.isPending) return
    if (isExitCommand(command)) {
      setExitConfirmOpen(true)
      return
    }

    clearToast()
    const animateCommand = isGitCommand(command)
    if (animateCommand) {
      dagAnimation.onCommandStart()
      battleDirector.onAttackStart()
    }

    const resolveTurn = (outcome: CommandSubmissionOutcome) => {
      if (!animateCommand) return
      dagAnimation.onCommandResolved(outcome)
      battleDirector.onResolve(battleEventsForSubmittedCommand({
        command,
        outcome,
        monsters: battleDirector.currentMonsters(),
        storyWorldSlug: runStorySlug(queryClient, runId),
      }))
    }
    const counts = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))?.counts
    let predicted: CommandSubmissionOutcome | null = null

    const execution = mutation.mutate(command, {
      onSuccess: (response) => {
        // A turn already played from the local outcome only replays when the
        // server judged it differently (it is the authority on progress).
        if (!predicted || !confirmsPrediction(predicted, response.command_outcome)) {
          resolveTurn(response.command_outcome)
        }
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
          const updatedRun = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))
          if (updatedRun) {
            evaluateAndNotify(updatedRun, response.step.command_classification)
          }
        }
      },
      onError: () => {
        if (!animateCommand) return
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
  const run = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))
  return run?.story?.world_slug ?? run?.story?.slug
}
