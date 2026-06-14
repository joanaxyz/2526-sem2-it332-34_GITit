import { useMutation, useQueryClient } from '@tanstack/react-query'

import { challengeRunsApi } from '@/features/challenges/api/challengeRunsApi'
import {
  invalidateLevelProgressQueries,
  syncChallengeRunInCache,
  updateChallengeRunCache,
} from '@/features/challenges/utils/challengeRunCache'
import type { ChallengeCommandResponse, ChallengeRun, ChallengeStepLog } from '@/shared/level/types'
import {
  createErrorStep as makeErrorStep,
  createPendingStep as makePendingStep,
  nextEphemeralStepId,
  stripEphemeralSteps,
} from '@/shared/level/terminalSteps'
import { queryKeys } from '@/shared/api/queryKeys'

type CommandMutationContext = {
  previous: ChallengeRun
  pendingId: number
}

// Challenge steps carry richer fields than the shared TerminalStep core; the
// optimistic placeholders fill them with empty values until the real step lands.
const challengeStepExtras = () => ({
  command_classification: '',
  contextual_feedback: '',
  created_at: new Date().toISOString(),
})

function createPendingStep(command: string, id: number): ChallengeStepLog {
  return { ...makePendingStep(command, id), ...challengeStepExtras() }
}

function createErrorStep(command: string, message: string, id: number): ChallengeStepLog {
  return { ...makeErrorStep(command, message, id), ...challengeStepExtras() }
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Command failed.'
}

export function useChallengeCommandSubmission(runId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (command: string) => challengeRunsApi.submitCommand(runId, command),
    onMutate: (command) => {
      const previous = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))
      if (!previous) return undefined

      const pendingId = nextEphemeralStepId()
      updateChallengeRunCache(queryClient, {
        ...previous,
        steps: [...stripEphemeralSteps(previous.steps), createPendingStep(command, pendingId)],
      })
      void queryClient.cancelQueries({ queryKey: queryKeys.challengeRun(runId) })

      return { previous, pendingId } satisfies CommandMutationContext
    },
    onSuccess: (response) => {
      const updatedRun = mergeCommandStepIntoRun(queryClient, response)
      updateChallengeRunCache(queryClient, updatedRun)

      if (!response.run.review_mode && response.run.status !== 'started') {
        syncChallengeRunInCache(queryClient, updatedRun)
        invalidateLevelProgressQueries(queryClient)
      }
    },
    onError: (error, command, context) => {
      if (!context?.previous) return

      updateChallengeRunCache(queryClient, {
        ...context.previous,
        steps: [
          ...stripEphemeralSteps(context.previous.steps),
          createErrorStep(command, errorMessage(error), nextEphemeralStepId()),
        ],
      })
    },
  })
}

function mergeCommandStepIntoRun(
  queryClient: ReturnType<typeof useQueryClient>,
  response: ChallengeCommandResponse,
): ChallengeRun {
  const previous = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(response.run.id))
  const priorSteps = stripEphemeralSteps(previous?.steps ?? [])
  const step = {
    id: response.step.id,
    command_text: response.step.command_text,
    terminal_output: response.step.terminal_output,
    result_category: response.step.result_category,
    command_classification: response.step.command_classification,
    contextual_feedback: response.step.contextual_feedback,
    created_at: response.step.created_at,
  }

  const hasCompletion = Object.prototype.hasOwnProperty.call(response.run, 'completion')
  const hasNextDifficulty = Object.prototype.hasOwnProperty.call(response.run, 'next_difficulty')
  const run: ChallengeRun = previous
    ? {
        ...previous,
        ...response.run,
        counts: {
          ...previous.counts,
          ...response.run.counts,
        },
        repository_state: mergeRepositoryState(previous.repository_state, response.run.repository_state),
        mastery_progress: response.run.mastery_progress ?? previous.mastery_progress,
        mastered_records: response.run.mastered_records ?? previous.mastered_records,
        completion: hasCompletion ? response.run.completion ?? null : previous.completion,
        next_difficulty: hasNextDifficulty ? response.run.next_difficulty ?? null : previous.next_difficulty,
      }
    : (response.run as ChallengeRun)

  return {
    ...run,
    steps: priorSteps.some((item) => item.id === step.id) ? priorSteps : [...priorSteps, step],
  }
}

function mergeRepositoryState(
  previous: ChallengeRun['repository_state'],
  next: ChallengeRun['repository_state'],
): ChallengeRun['repository_state'] {
  // The command response carries the tree only when it changed; an absent tree
  // means "unchanged", so we fall back to the previous one below. (Checking the
  // keys' length would be redundant: a present tree is authoritative even when
  // empty - e.g. a freshly cleared workspace.)
  const carriesTree = next.project_tree !== undefined || next.visible_tree !== undefined
  if (carriesTree) {
    return next
  }

  return {
    ...next,
    project_tree: previous.project_tree,
    visible_tree: previous.visible_tree,
  }
}
