import type { QueryClient } from '@tanstack/react-query'

import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import type { ChallengeDagAnimationController } from '@/features/challenges/hooks/useChallengeDagAnimation'
import type { ChallengeRun } from '@/features/challenges/types'
import { stringList } from '@/features/challenges/components/challengeWorkspaceLayout'
import { queryKeys } from '@/shared/api/queryKeys'
import {
  confirmsPrediction,
  predictLocalOutcome,
  type CommandSubmissionOutcome,
} from '@/shared/level-runtime/commandOutcome'
import { isExitCommand } from '@/shared/level-runtime/commands'

export function createChallengeWorkspaceCommandHandler({
  runId,
  mutation,
  dagAnimation,
  queryClient,
  clearToast,
  evaluateAndNotify,
  setExitConfirmOpen,
  setWorkspaceEditorPath,
  queueOutcomeAnimation,
}: {
  runId: number
  mutation: ReturnType<typeof useChallengeCommandSubmission>
  dagAnimation: ChallengeDagAnimationController
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
    dagAnimation.onCommandStart()

    const counts = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))?.counts
    let predicted: CommandSubmissionOutcome | null = null

    const execution = mutation.mutate(command, {
      onSuccess: (response) => {
        // A turn already shown from the local outcome only replays when the
        // server judged it differently (it is the authority on progress).
        if (!predicted || !confirmsPrediction(predicted, response.command_outcome)) {
          dagAnimation.onCommandResolved(response.command_outcome)
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
      onError: () => dagAnimation.onCommandError(),
    })
    // Misses and read-only looks need no server verdict.
    predicted = execution && counts
      ? predictLocalOutcome(execution, {
          counted: counts.counted_action_total,
          max: counts.maximum_counted_commands,
        })
      : null
    if (predicted) dagAnimation.onCommandResolved(predicted)
  }
}
