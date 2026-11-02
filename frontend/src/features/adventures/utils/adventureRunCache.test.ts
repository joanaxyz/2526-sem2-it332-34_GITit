import { QueryClient } from '@tanstack/react-query'
import { describe, expect, it } from 'vitest'

import { mergeCommandRun } from '@/features/adventures/hooks/useAdventureCommandSubmission'
import type { AdventureRun, AdventureRunPatch } from '@/features/adventures/types'
import { queryKeys } from '@/shared/api/queryKeys'

import { syncAdventureRunInCache } from './adventureRunCache'

function adventureRun(id: number): AdventureRun {
  return { id } as unknown as AdventureRun
}

describe('syncAdventureRunInCache', () => {
  it('invalidates story adventure summaries when a run changes', () => {
    const queryClient = new QueryClient()
    const run = adventureRun(42)
    const chaptersKey = queryKeys.storyChapters('arcane-spire')
    const overviewKey = queryKeys.chapterOverview(7)

    queryClient.setQueryData(chaptersKey, [])
    queryClient.setQueryData(overviewKey, { adventures: [{ latest_run_id: 42 }] })

    syncAdventureRunInCache(queryClient, run)

    expect(queryClient.getQueryData(queryKeys.adventureRun(42))).toBe(run)
    expect(queryClient.getQueryState(chaptersKey)?.isInvalidated).toBe(true)
    expect(queryClient.getQueryState(overviewKey)?.isInvalidated).toBe(true)
  })
})

describe('mergeCommandRun', () => {
  it('retains the cached project tree when a command patch omits it', () => {
    const previous = {
      id: 42,
      status: 'started',
      current_attempt: {
        id: 7,
        counts: { command_count: 0, counted_command_count: 0 },
        repository_state: {
          commits: [],
          branches: { main: null },
          head: { type: 'branch', name: 'main', target: null },
          staging: {},
          working_tree: {},
          conflicts: [],
          project_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'hello' },
          },
          visible_tree: {
            'README.md': { status: 'clean', source: 'head', content: 'hello' },
          },
        },
      },
    } as unknown as AdventureRun
    const patch = {
      partial: true,
      id: 42,
      status: 'started',
      current_attempt: {
        id: 7,
        counts: { command_count: 1, counted_command_count: 0 },
        repository_state: {
          commits: [],
          branches: { main: null },
          head: { type: 'branch', name: 'main', target: null },
          staging: {},
          working_tree: {},
          conflicts: [],
        },
        objective_checks: null,
      },
    } as unknown as AdventureRunPatch

    const merged = mergeCommandRun(previous, patch)

    expect(merged?.current_attempt?.repository_state.project_tree).toEqual(
      previous.current_attempt?.repository_state.project_tree,
    )
    expect(merged?.current_attempt?.counts.command_count).toBe(1)
  })
})
