import { useMutation, useQueryClient } from '@tanstack/react-query'

import { commandAdventuresApi } from '@/features/command-adventures/api/commandAdventuresApi'
import type {
  AdventureAttempt,
  AdventureRun,
  AdventureRunPatch,
  AdventureStepLog,
} from '@/features/command-adventures/types'
import {
  createErrorStep,
  createPendingStep,
  nextEphemeralStepId,
  stripEphemeralSteps,
} from '@/shared/level/terminalSteps'
import { queryKeys } from '@/shared/api/queryKeys'

function isRunPatch(run: AdventureRun | AdventureRunPatch): run is AdventureRunPatch {
  return (run as AdventureRunPatch).partial === true
}

function mergeAttempt(
  prev: AdventureAttempt,
  patch: NonNullable<AdventureRunPatch['current_attempt']>,
): AdventureAttempt {
  const checks = patch.objective_checks
  return {
    ...prev,
    counts: patch.counts,
    repository_state: patch.repository_state,
    // Only the live checklist changes mid-attempt; the authored brief
    // (scenario_context) is never touched. An empty/absent checklist keeps the
    // prior rows so a sparse patch can't blank out the panel.
    objective_checks: checks && checks.length > 0 ? checks : prev.objective_checks,
  }
}

// A slim patch updates only the live attempt of an already-cached run; a full
// run (transition) replaces it outright. Returns null when a patch arrives with
// no cached run to merge into (caller refetches). The live attempt's `steps`
// array is preserved across a patch merge so the optimistic placeholder survives.
export function mergeCommandRun(
  previous: AdventureRun | undefined,
  next: AdventureRun | AdventureRunPatch,
): AdventureRun | null {
  if (!isRunPatch(next)) return next
  if (!previous) return null
  const sameAttempt =
    previous.current_attempt &&
    next.current_attempt &&
    previous.current_attempt.id === next.current_attempt.id
  return {
    ...previous,
    status: next.status,
    current_attempt: sameAttempt
      ? mergeAttempt(previous.current_attempt as AdventureAttempt, next.current_attempt!)
      : previous.current_attempt,
  }
}

function writeAttemptSteps(run: AdventureRun, steps: AdventureStepLog[]): AdventureRun {
  if (!run.current_attempt) return run
  return { ...run, current_attempt: { ...run.current_attempt, steps } }
}

/**
 * Submits a command and drives the terminal optimistically, mirroring the
 * challenge flow: a `Pending` placeholder is inserted the instant the user hits
 * Run (so the terminal shows `cmd` + `…` with no round-trip wait), then replaced
 * by the persisted step on success. A transition (solved / budget spent) returns
 * a full run whose next attempt has its own empty step list, which naturally
 * resets the terminal for the next problem.
 */
export function useAdventureCommandSubmission(runId: number | null) {
  const queryClient = useQueryClient()
  const key = queryKeys.adventureRun(runId as number)

  return useMutation({
    mutationFn: (command: string) => commandAdventuresApi.submitCommand(runId as number, command),
    onMutate: (command) => {
      const previous = queryClient.getQueryData<AdventureRun>(key)
      if (!previous?.current_attempt) return { previous }

      const pendingId = nextEphemeralStepId()
      const steps = [
        ...stripEphemeralSteps(previous.current_attempt.steps ?? []),
        createPendingStep(command, pendingId),
      ]
      queryClient.setQueryData(key, writeAttemptSteps(previous, steps))
      void queryClient.cancelQueries({ queryKey: key })
      return { previous }
    },
    onSuccess: (response) => {
      const previous = queryClient.getQueryData<AdventureRun>(key)
      // Mid-attempt patches (`partial: true`) never carry `is_passed`; only a
      // full run payload can signal a fresh pass that mints coins.
      const run = response.run
      const earnedCoins =
        (!('partial' in run) && run.is_passed && previous && !previous.is_passed) ||
        (run.status === 'completed' && previous?.status !== 'completed')
      if (earnedCoins) {
        void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
      }
      const merged = mergeCommandRun(previous, response.run)
      if (!merged) {
        void queryClient.invalidateQueries({ queryKey: key })
        return
      }

      const sameAttempt =
        previous?.current_attempt &&
        merged.current_attempt &&
        previous.current_attempt.id === merged.current_attempt.id

      if (sameAttempt && merged.current_attempt) {
        // Mid-attempt: drop the optimistic placeholder, append the persisted step.
        const base = stripEphemeralSteps(merged.current_attempt.steps ?? [])
        const steps = base.some((step) => step.id === response.step.id)
          ? base
          : [...base, response.step]
        queryClient.setQueryData(key, writeAttemptSteps(merged, steps))
      } else {
        // Transition: the full run carries the next attempt (with its own empty
        // step list), so the placeholder is discarded and the terminal resets.
        queryClient.setQueryData(key, merged)
      }
    },
    onError: (_error, command, context) => {
      const previous = context?.previous
      if (!previous?.current_attempt) return
      const steps = [
        ...stripEphemeralSteps(previous.current_attempt.steps ?? []),
        createErrorStep(command, 'Command failed. Please try again.', nextEphemeralStepId()),
      ]
      queryClient.setQueryData(key, writeAttemptSteps(previous, steps))
    },
  })
}
