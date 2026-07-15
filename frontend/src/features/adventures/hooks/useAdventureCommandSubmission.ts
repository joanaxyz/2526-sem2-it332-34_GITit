import type { QueryClient } from '@tanstack/react-query'

import { adventuresApi } from '@/features/adventures/api/adventuresApi'
import type { AdventureAttempt, AdventureCommandResponse, AdventureRun, AdventureRunPatch, AdventureStepLog } from '@/features/adventures/types'
import { invalidateAdventureProgressQueries } from '@/features/adventures/utils/adventureRunCache'
import { queryKeys } from '@/shared/api/queryKeys'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { createErrorStep, createPendingStep } from '@/shared/level/terminalSteps'
import type { RepositorySnapshot } from '@/shared/level/types'
import { mergeRepositoryState } from '@/shared/level-runtime/repositoryState'
import { useOptimisticGitCommand } from '@/shared/level-runtime/useOptimisticGitCommand'

function isRunPatch(run: AdventureRun | AdventureRunPatch): run is AdventureRunPatch {
  return (run as AdventureRunPatch).partial === true
}

function mergeAttempt(prev: AdventureAttempt, patch: NonNullable<AdventureRunPatch['current_attempt']>): AdventureAttempt {
  const checks = patch.objective_checks
  return {
    ...prev,
    counts: patch.counts,
    repository_state: mergeRepositoryState(prev.repository_state, patch.repository_state),
    objective_checks: checks && checks.length > 0 ? checks : prev.objective_checks,
  }
}

export function mergeCommandRun(previous: AdventureRun | undefined, next: AdventureRun | AdventureRunPatch): AdventureRun | null {
  if (!isRunPatch(next)) return next
  if (!previous) return null
  const sameAttempt = previous.current_attempt && next.current_attempt && previous.current_attempt.id === next.current_attempt.id
  return {
    ...previous,
    status: next.status,
    current_attempt: sameAttempt ? mergeAttempt(previous.current_attempt as AdventureAttempt, next.current_attempt!) : previous.current_attempt,
  }
}

function writeAttemptSteps(run: AdventureRun, steps: AdventureStepLog[]): AdventureRun {
  if (!run.current_attempt) return run
  return { ...run, current_attempt: { ...run.current_attempt, steps } }
}

function createLocalStep(command: string, output: string, id: number): AdventureStepLog {
  return { id, command_text: command, terminal_output: output, result_category: 'Local' }
}

function applyOptimisticState(run: AdventureRun, repositoryState: RepositorySnapshot, steps: AdventureStepLog[]): AdventureRun {
  if (!run.current_attempt) return run
  return { ...run, current_attempt: { ...run.current_attempt, repository_state: repositoryState, steps } }
}

function applyResponse(queryClient: QueryClient, key: ReturnType<typeof queryKeys.adventureRun>, response: AdventureCommandResponse) {
  const previous = queryClient.getQueryData<AdventureRun>(key)
  const payload = response.run
  const earnedCoins =
    (!('partial' in payload) && payload.is_passed && previous && !previous.is_passed) ||
    (payload.status === 'completed' && previous?.status !== 'completed')
  if (earnedCoins) void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })

  const merged = mergeCommandRun(previous, payload)
  if (!merged) {
    void queryClient.invalidateQueries({ queryKey: key })
    return
  }
  if (!isRunPatch(payload)) invalidateAdventureProgressQueries(queryClient)

  const sameAttempt = previous?.current_attempt && merged.current_attempt && previous.current_attempt.id === merged.current_attempt.id
  if (sameAttempt && merged.current_attempt) {
    const base = merged.current_attempt.steps.filter((step) => step.id >= 0)
    const steps = base.some((step) => step.id === response.step.id) ? base : [...base, response.step]
    queryClient.setQueryData(key, writeAttemptSteps(merged, steps))
  } else {
    queryClient.setQueryData(key, merged)
  }
}

export function useAdventureCommandSubmission(runId: number | null) {
  const key = queryKeys.adventureRun(runId as number)
  return useOptimisticGitCommand<AdventureRun, AdventureStepLog, AdventureCommandResponse>({
    queryKey: key,
    readSession: (run) => {
      const attempt = run.current_attempt
      if (!attempt) return null
      return {
        repositoryState: attempt.repository_state as MutableRepositoryState,
        revision: attempt.counts.command_count,
        steps: attempt.steps ?? [],
      }
    },
    applyOptimisticState,
    replaceSteps: writeAttemptSteps,
    createPendingStep,
    createLocalStep,
    createErrorStep,
    submit: (command, execution) => adventuresApi.submitCommand(runId as number, command, execution),
    onSuccess: (response, _previous, queryClient) => applyResponse(queryClient, key, response),
    noSessionMessage: 'No adventure attempt is available to execute this command.',
  })
}
