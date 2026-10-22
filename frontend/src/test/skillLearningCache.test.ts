import { QueryClient } from '@tanstack/react-query'
import { cleanup, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import type { TierCommandResponse, TierRun, TierStepLog } from '@/features/story-map/components/tierWorkspaceTypes'
import { queryKeys } from '@/shared/api/queryKeys'
import type { OptimisticGitCommandConfig } from '@/shared/level-runtime/useOptimisticGitCommand'

const mocks = vi.hoisted(() => ({ optimistic: vi.fn() }))
vi.mock('@/shared/level-runtime/useOptimisticGitCommand', () => ({ useOptimisticGitCommand: mocks.optimistic }))

const skill = { id: 7, slug: 'git-init', title: 'Create a repository', base_command: 'git init', summary: '', chapter_number: 1, chapter_title: 'Foundations' }

afterEach(() => { cleanup(); vi.clearAllMocks() })

describe('learned skill cache updates on command responses', () => {
  it.each([true, false])('refreshes the spellbook only for a tier learning event while the run is still started (event=%s)', (learned) => {
    renderHook(() => useTierCommandSubmission(1))
    const config = mocks.optimistic.mock.calls[0][0] as OptimisticGitCommandConfig<TierRun, TierStepLog, TierCommandResponse>
    const queryClient = new QueryClient()
    const invalidate = vi.spyOn(queryClient, 'invalidateQueries')
    const response = { run: { id: 1, status: 'started', replay: false }, step: { id: 3 }, learned_skills: learned ? [skill] : [] } as unknown as TierCommandResponse
    config.onSuccess(response, undefined, queryClient)
    const spellbookCalls = invalidate.mock.calls.filter(([filters]) => filters?.queryKey === queryKeys.learnedSkills)
    expect(spellbookCalls).toHaveLength(learned ? 1 : 0)
  })
})
