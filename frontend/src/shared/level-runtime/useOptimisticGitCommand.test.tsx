import { createElement, type ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { createErrorStep, createPendingStep } from '@/shared/level/terminalSteps'
import type { CommandExecutionPayload, RepositorySnapshot, TerminalStep } from '@/shared/level/types'
import { useOptimisticGitCommand } from '@/shared/level-runtime/useOptimisticGitCommand'

type Run = { repository_state: RepositorySnapshot; revision: number; steps: TerminalStep[] }

const KEY = ['optimistic-command-test']

function setup(submit: (command: string, execution: CommandExecutionPayload) => Promise<{ ok: true }>) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  queryClient.setQueryData<Run>(KEY, {
    repository_state: { repository_initialized: false } as RepositorySnapshot,
    revision: 3,
    steps: [],
  })
  const wrapper = ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children)
  const { result } = renderHook(
    () =>
      useOptimisticGitCommand<Run, TerminalStep, { ok: true }>({
        queryKey: KEY,
        readSession: (run) => ({
          repositoryState: run.repository_state as MutableRepositoryState,
          revision: run.revision,
          steps: run.steps,
        }),
        applyOptimisticState: (run, repositoryState, steps) => ({ ...run, repository_state: repositoryState, steps }),
        replaceSteps: (run, steps) => ({ ...run, steps }),
        createPendingStep,
        createLocalStep: (command, output, id) => ({ id, command_text: command, terminal_output: output, result_category: 'Local' }),
        createErrorStep,
        submit,
        onSuccess: () => undefined,
        noSessionMessage: 'No run.',
      }),
    { wrapper },
  )
  return { queryClient, result }
}

describe('useOptimisticGitCommand', () => {
  it('shows the command and sends it before anything renders', () => {
    const submit = vi.fn<(command: string, execution: CommandExecutionPayload) => Promise<{ ok: true }>>(() => new Promise<{ ok: true }>(() => undefined))
    const { queryClient, result } = setup(submit)

    let execution: CommandExecutionPayload | null = null
    act(() => {
      execution = result.current.mutate('git init')
      // Same tick as Enter: the request is out and the cache already holds it.
      expect(submit).toHaveBeenCalledTimes(1)
      expect(queryClient.getQueryData<Run>(KEY)?.repository_state.repository_initialized).toBe(true)
      expect(queryClient.getQueryData<Run>(KEY)?.steps.at(-1)?.command_text).toBe('git init')
    })
    expect(execution).toMatchObject({ processed: true, client_run_revision: 3 })
    expect(submit.mock.calls[0][1]).toBe(execution)
  })

  it('waits for an in-flight refetch to be cancelled before going optimistic', async () => {
    const submit = vi.fn(() => new Promise<{ ok: true }>(() => undefined))
    const { queryClient, result } = setup(submit)
    void queryClient.fetchQuery({ queryKey: KEY, queryFn: () => new Promise<Run>(() => undefined) })

    let execution: CommandExecutionPayload | null = null
    act(() => {
      execution = result.current.mutate('git init')
    })
    expect(execution).toBeNull()
    await waitFor(() => expect(submit).toHaveBeenCalledTimes(1))
    expect(queryClient.getQueryData<Run>(KEY)?.repository_state.repository_initialized).toBe(true)
  })

  it('restores the run and reports the error when the server rejects the command', async () => {
    const { queryClient, result } = setup(() => Promise.reject(new Error('rejected')))

    act(() => {
      result.current.mutate('git init')
    })
    await waitFor(() => expect(queryClient.getQueryData<Run>(KEY)?.steps.at(-1)?.result_category).toBe('Error'))
    expect(queryClient.getQueryData<Run>(KEY)?.repository_state.repository_initialized).toBe(false)
  })
})
