import type { QueryClient } from '@tanstack/react-query'

import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { stringList } from '@/features/story-map/components/tierWorkspaceLayout'
import { queryKeys } from '@/shared/api/queryKeys'
import { isExitCommand } from '@/shared/level-runtime/commands'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { battleEventsForSubmittedCommand } from '@/shared/level-runtime/commandBattle'

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

    mutation.mutate(command, {
      onSuccess: (response) => {
        dagAnimation.onCommandResolved(response.command_outcome)
        battleDirector.onResolve(battleEventsForSubmittedCommand({
          command,
          outcome: response.command_outcome,
          monsters: battleDirector.currentMonsters(),
          storyWorldSlug: runStorySlug(queryClient, runId),
        }))
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
  }
}

function runStorySlug(queryClient: QueryClient, runId: number) {
  const run = queryClient.getQueryData<TierRun>(queryKeys.adventureTierRun(runId))
  return run?.story?.world_slug ?? run?.story?.slug
}
