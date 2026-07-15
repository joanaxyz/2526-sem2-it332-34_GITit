import type { QueryClient } from '@tanstack/react-query'

import { challengeRunsApi } from '@/features/challenges/api/challengeRunsApi'
import type { ChallengeCommandResponse, ChallengeRun, ChallengeStepLog } from '@/features/challenges/types'
import { invalidateLevelProgressQueries, syncChallengeRunInCache, updateChallengeRunCache } from '@/features/challenges/utils/challengeRunCache'
import { queryKeys } from '@/shared/api/queryKeys'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { createErrorStep as makeErrorStep, createPendingStep as makePendingStep } from '@/shared/level/terminalSteps'
import type { RepositorySnapshot } from '@/shared/level/types'
import { mergeRepositoryState } from '@/shared/level-runtime/repositoryState'
import { useOptimisticGitCommand } from '@/shared/level-runtime/useOptimisticGitCommand'

const challengeStepExtras = () => ({ command_classification: '', contextual_feedback: '', created_at: new Date().toISOString() })
function createPendingStep(command: string, id: number): ChallengeStepLog { return { ...makePendingStep(command, id), ...challengeStepExtras() } }
function createLocalStep(command: string, output: string, id: number): ChallengeStepLog {
  return { id, command_text: command, terminal_output: output, result_category: 'Local', ...challengeStepExtras() }
}
function createErrorStep(command: string, message: string, id: number): ChallengeStepLog { return { ...makeErrorStep(command, message, id), ...challengeStepExtras() } }
function applyOptimisticState(run: ChallengeRun, repositoryState: RepositorySnapshot, steps: ChallengeStepLog[]): ChallengeRun {
  return { ...run, repository_state: repositoryState, steps }
}
function replaceSteps(run: ChallengeRun, steps: ChallengeStepLog[]): ChallengeRun { return { ...run, steps } }

function applyResponse(queryClient: QueryClient, response: ChallengeCommandResponse) {
  const updatedRun = mergeCommandStepIntoRun(queryClient, response)
  updateChallengeRunCache(queryClient, updatedRun)
  if (!response.run.replay && response.run.status !== 'started') {
    syncChallengeRunInCache(queryClient, updatedRun)
    invalidateLevelProgressQueries(queryClient)
  }
}

export function useChallengeCommandSubmission(runId: number) {
  const key = queryKeys.challengeRun(runId)
  return useOptimisticGitCommand<ChallengeRun, ChallengeStepLog, ChallengeCommandResponse>({
    queryKey: key,
    readSession: (run) => ({ repositoryState: run.repository_state as MutableRepositoryState, revision: run.counts.total_attempts, steps: run.steps }),
    applyOptimisticState,
    replaceSteps,
    createPendingStep,
    createLocalStep,
    createErrorStep,
    submit: (command, execution) => challengeRunsApi.submitCommand(runId, command, execution),
    onSuccess: (response, _previous, queryClient) => applyResponse(queryClient, response),
    noSessionMessage: 'No challenge run is available to execute this command.',
  })
}

function mergeCommandStepIntoRun(queryClient: QueryClient, response: ChallengeCommandResponse): ChallengeRun {
  const previous = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(response.run.id))
  const priorSteps = (previous?.steps ?? []).filter((step) => step.id >= 0)
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
  const run: ChallengeRun = previous ? {
    ...previous,
    ...response.run,
    counts: { ...previous.counts, ...response.run.counts },
    repository_state: mergeRepositoryState(previous.repository_state, response.run.repository_state),
    mastery_progress: response.run.mastery_progress ?? previous.mastery_progress,
    completion: hasCompletion ? response.run.completion ?? null : previous.completion,
    next_difficulty: hasNextDifficulty ? response.run.next_difficulty ?? null : previous.next_difficulty,
  } : (response.run as ChallengeRun)
  return { ...run, steps: priorSteps.some((item) => item.id === step.id) ? priorSteps : [...priorSteps, step] }
}
