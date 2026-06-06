import { useMutation, useQueryClient } from '@tanstack/react-query'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { reviewApi } from '@/features/review/api/reviewApi'
import {
  invalidateScenarioProgressQueries,
  syncPracticeSessionInCache,
  updatePracticeSessionCache,
} from '@/features/scenarios/utils/scenarioCache'
import type { CommandResponse, PracticeSession, PracticeStepLog } from '@/features/practice/types'
import { queryKeys } from '@/shared/api/queryKeys'

type CommandMutationContext = {
  previous: PracticeSession
  pendingId: number
}

let ephemeralStepId = 0

function nextEphemeralStepId() {
  ephemeralStepId -= 1
  return ephemeralStepId
}

export function isEphemeralStep(step: PracticeStepLog) {
  return step.id < 0
}

export function stripEphemeralSteps(steps: PracticeStepLog[]) {
  return steps.filter((step) => !isEphemeralStep(step))
}

function createPendingStep(command: string, id: number): PracticeStepLog {
  return {
    id,
    command_text: command,
    terminal_output: '',
    result_category: 'Pending',
    command_classification: '',
    contextual_feedback: '',
    created_at: new Date().toISOString(),
  }
}

function createErrorStep(command: string, message: string, id: number): PracticeStepLog {
  return {
    id,
    command_text: command,
    terminal_output: message,
    result_category: 'Error',
    command_classification: '',
    contextual_feedback: '',
    created_at: new Date().toISOString(),
  }
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Command failed.'
}

export function useCommandSubmission(sessionId: number, reviewMode: boolean) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (command: string) =>
      reviewMode ? reviewApi.submitCommand(sessionId, command) : practiceApi.submitCommand(sessionId, command),
    onMutate: (command) => {
      const previous = queryClient.getQueryData<PracticeSession>(queryKeys.practiceSession(sessionId))
      if (!previous) return undefined

      const pendingId = nextEphemeralStepId()
      updatePracticeSessionCache(queryClient, {
        ...previous,
        steps: [...stripEphemeralSteps(previous.steps), createPendingStep(command, pendingId)],
      })
      void queryClient.cancelQueries({ queryKey: queryKeys.practiceSession(sessionId) })

      return { previous, pendingId } satisfies CommandMutationContext
    },
    onSuccess: (response) => {
      const updatedSession = mergeCommandStepIntoSession(queryClient, response)
      updatePracticeSessionCache(queryClient, updatedSession)

      if (!reviewMode && response.session.status !== 'started') {
        syncPracticeSessionInCache(queryClient, updatedSession)
        invalidateScenarioProgressQueries(queryClient)
      }
    },
    onError: (error, command, context) => {
      if (!context?.previous) return

      updatePracticeSessionCache(queryClient, {
        ...context.previous,
        steps: [
          ...stripEphemeralSteps(context.previous.steps),
          createErrorStep(command, errorMessage(error), nextEphemeralStepId()),
        ],
      })
    },
  })
}

function mergeCommandStepIntoSession(
  queryClient: ReturnType<typeof useQueryClient>,
  response: CommandResponse,
): PracticeSession {
  const previous = queryClient.getQueryData<PracticeSession>(queryKeys.practiceSession(response.session.id))
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

  const hasCompletion = Object.prototype.hasOwnProperty.call(response.session, 'completion')
  const hasNextDifficulty = Object.prototype.hasOwnProperty.call(response.session, 'next_difficulty')
  const session: PracticeSession = previous
    ? {
        ...previous,
        ...response.session,
        counts: {
          ...previous.counts,
          ...response.session.counts,
        },
        repository_state: mergeRepositoryState(previous.repository_state, response.session.repository_state),
        mastery_progress: response.session.mastery_progress ?? previous.mastery_progress,
        mastered_records: response.session.mastered_records ?? previous.mastered_records,
        completion: hasCompletion ? response.session.completion ?? null : previous.completion,
        next_difficulty: hasNextDifficulty ? response.session.next_difficulty ?? null : previous.next_difficulty,
      }
    : (response.session as PracticeSession)

  return {
    ...session,
    steps: priorSteps.some((item) => item.id === step.id) ? priorSteps : [...priorSteps, step],
  }
}

function mergeRepositoryState(
  previous: PracticeSession['repository_state'],
  next: PracticeSession['repository_state'],
): PracticeSession['repository_state'] {
  const hasProjectTree =
    next.project_tree !== undefined ||
    next.visible_tree !== undefined ||
    Object.keys(next.project_tree ?? {}).length > 0 ||
    Object.keys(next.visible_tree ?? {}).length > 0

  if (hasProjectTree) {
    return next
  }

  return {
    ...next,
    project_tree: previous.project_tree,
    visible_tree: previous.visible_tree,
  }
}
