import { useRef } from 'react'
import { useMutation, useQueryClient, type QueryClient, type QueryKey } from '@tanstack/react-query'

import { ApiError } from '@/shared/api/apiError'
import { executeGitCommand } from '@/shared/git/simulator/engine'
import { snapshot } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { withClientRunRevision } from '@/shared/level/commandExecution'
import { nextEphemeralStepId, stripEphemeralSteps } from '@/shared/level/terminalSteps'
import type { CommandExecutionPayload, RepositorySnapshot, TerminalStep } from '@/shared/level/types'

export type OptimisticCommandSession<TStep extends TerminalStep> = {
  repositoryState: MutableRepositoryState
  revision: number
  steps: TStep[]
}

type MutationContext<TRun> = { previous?: TRun }

// Surface the backend's rejection reason (DRF `detail`) in the terminal so a
// refused command explains itself; server faults stay behind a generic retry.
function defaultErrorMessage(error: unknown): string {
  if (error instanceof ApiError && error.status < 500 && error.message) return error.message
  return 'Command failed. Please try again.'
}

export type OptimisticGitCommandConfig<TRun, TStep extends TerminalStep, TResponse> = {
  queryKey: QueryKey
  readSession: (run: TRun) => OptimisticCommandSession<TStep> | null
  applyOptimisticState: (run: TRun, repositoryState: RepositorySnapshot, steps: TStep[]) => TRun
  replaceSteps: (run: TRun, steps: TStep[]) => TRun
  createPendingStep: (command: string, id: number) => TStep
  createLocalStep: (command: string, output: string, id: number) => TStep
  createErrorStep: (command: string, message: string, id: number) => TStep
  submit: (command: string, execution: CommandExecutionPayload) => Promise<TResponse>
  onSuccess: (response: TResponse, previous: TRun | undefined, queryClient: QueryClient) => void
  noSessionMessage: string
}

/** Shared optimistic command lifecycle for adventure and challenge runs. */
export function useOptimisticGitCommand<TRun, TStep extends TerminalStep, TResponse>(
  config: OptimisticGitCommandConfig<TRun, TStep, TResponse>,
) {
  const queryClient = useQueryClient()
  const pendingExecutionRef = useRef<CommandExecutionPayload | null>(null)

  return useMutation<TResponse, unknown, string, MutationContext<TRun>>({
    mutationFn: (command) => {
      const pending = pendingExecutionRef.current
      if (pending) return config.submit(command, pending)
      const current = queryClient.getQueryData<TRun>(config.queryKey)
      const session = current ? config.readSession(current) : null
      if (!session) throw new Error(config.noSessionMessage)
      return config.submit(
        command,
        withClientRunRevision(executeGitCommand(session.repositoryState, command), session.revision),
      )
    },
    onMutate: async (command) => {
      await queryClient.cancelQueries({ queryKey: config.queryKey })
      const previous = queryClient.getQueryData<TRun>(config.queryKey)
      const session = previous ? config.readSession(previous) : null
      if (!previous || !session) return { previous }

      const id = nextEphemeralStepId()
      const execution = withClientRunRevision(
        executeGitCommand(session.repositoryState, command),
        session.revision,
      )
      pendingExecutionRef.current = execution
      const steps = [
        ...stripEphemeralSteps(session.steps),
        execution.output
          ? config.createLocalStep(command, execution.output, id)
          : config.createPendingStep(command, id),
      ]
      queryClient.setQueryData(
        config.queryKey,
        config.applyOptimisticState(previous, snapshot(execution.next_state, true), steps),
      )
      return { previous }
    },
    onSuccess: (response, _command, context) => {
      pendingExecutionRef.current = null
      config.onSuccess(response, context?.previous, queryClient)
    },
    onError: (error, command, context) => {
      pendingExecutionRef.current = null
      const previous = context?.previous
      const session = previous ? config.readSession(previous) : null
      if (!previous || !session) return
      const message = defaultErrorMessage(error)
      queryClient.setQueryData(
        config.queryKey,
        config.replaceSteps(previous, [
          ...stripEphemeralSteps(session.steps),
          config.createErrorStep(command, message, nextEphemeralStepId()),
        ]),
      )
    },
  })
}
