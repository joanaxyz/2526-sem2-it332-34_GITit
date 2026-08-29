import { useAdventureCommandSubmission } from '@/features/adventures/hooks/useAdventureCommandSubmission'
import type { AdventureAttempt, AdventureRun } from '@/features/adventures/types'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { TerminalLine } from '@/shared/level/types'
import { battleEventsForSubmittedCommand } from '@/shared/level-runtime/commandBattle'
import { isExitCommand } from '@/shared/level-runtime/commands'

type AdventureWorkspaceSnapshot = {
  run: AdventureRun
  lines: TerminalLine[]
}

export function createAdventureWorkspaceCommandHandler({
  attempt,
  run,
  lines,
  submitCommand,
  director,
  setExitConfirmOpen,
  setLastWorkspace,
  queueOutcomeAnimation,
}: {
  attempt: AdventureAttempt | null | undefined
  run: AdventureRun
  lines: TerminalLine[]
  submitCommand: ReturnType<typeof useAdventureCommandSubmission>
  director: ReturnType<typeof useBattleDirector>
  setExitConfirmOpen: (open: boolean) => void
  setLastWorkspace: (snapshot: AdventureWorkspaceSnapshot) => void
  queueOutcomeAnimation: (runId: number) => void
}) {
  return (command: string) => {
    if (!attempt || run.status !== 'started') return
    if (isExitCommand(command)) {
      setExitConfirmOpen(true)
      return
    }
    // Drop a command fired while the previous one is still in flight (fast
    // double-tap / Enter race): submitting two for the same attempt collides on
    // the row lock server-side and would be rejected anyway.
    if (submitCommand.isPending) return
    setLastWorkspace({ run, lines })
    director.onAttackStart()
    submitCommand.mutate(command, {
      onSuccess: (response) => {
        const finishRunStatus = response.run.status
        const finishRunId = 'partial' in response.run ? run.id : response.run.id
        const responseStory = 'story' in response.run ? response.run.story : null
        director.onResolve(battleEventsForSubmittedCommand({
          command,
          outcome: response.command_outcome,
          monsters: director.currentMonsters(),
          storyWorldSlug:
            responseStory?.world_slug ?? responseStory?.slug ?? run.story?.world_slug ?? run.story?.slug,
        }))
        if (finishRunStatus === 'completed' || finishRunStatus === 'failed') {
          queueOutcomeAnimation(finishRunId)
        }
      },
      onError: () => director.onError(),
    })
  }
}
