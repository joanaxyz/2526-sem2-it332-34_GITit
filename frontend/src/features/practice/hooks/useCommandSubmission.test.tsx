import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { practiceApi } from '@/features/practice/api/practiceApi'
import type { CommandResponse, ScenarioSession } from '@/features/practice/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { useCommandSubmission } from './useCommandSubmission'

vi.mock('@/features/practice/api/practiceApi', () => ({
  practiceApi: {
    submitCommand: vi.fn(),
  },
}))

vi.mock('@/features/review/api/reviewApi', () => ({
  reviewApi: {
    submitCommand: vi.fn(),
  },
}))

const baseSession: ScenarioSession = {
  id: 42,
  mode: 'primary',
  status: 'completed',
  difficulty_instance_id: 7,
  completed_at: '2026-05-18T12:00:00Z',
  first_attempt_star_eligible: true,
  completion_type: 'state_based',
  scenario: {
    id: 5,
    slug: 'inspect-state',
    title: 'Inspect the repository',
    focus: 'git status',
    narrative: '',
  },
  module: {
    id: 3,
    number: 1,
    title: 'Basics',
  },
  difficulty: 'easy',
  variant: {
    id: 9,
    label: 'Variant A',
    changed_variant: false,
  },
  mastery_progress: {
    mastered: 1,
    required: 1,
  },
  policy: {
    id: 11,
    min_counted_commands: 1,
    max_counted_commands: 3,
    non_counted_patterns: [],
  },
  counts: {
    counted_action_total: 1,
    minimum_counted_commands: 1,
    maximum_counted_commands: 3,
    non_counted_diagnostic_total: 0,
    remaining_counted_commands: 2,
    max_reached: false,
    total_attempts: 1,
  },
  scaffolding: {
    live_dag: true,
    expected_state: true,
    contextual_feedback: true,
  },
  repository_state: {
    commits: [],
    branches: { main: null },
    head: { type: 'branch', name: 'main', target: null },
    staging: {},
    working_tree: {},
    conflicts: [],
  },
  expected_state: null,
  steps: [],
  review_mode: false,
  next_difficulty: null,
  completion: null,
}

const startedResponse: CommandResponse = {
  session: {
    id: baseSession.id,
    mode: baseSession.mode,
    status: 'started',
    difficulty_instance_id: baseSession.difficulty_instance_id,
    completed_at: null,
    first_attempt_star_eligible: false,
    counts: {
      ...baseSession.counts,
      counted_action_total: 0,
      non_counted_diagnostic_total: 1,
      remaining_counted_commands: 3,
      total_attempts: 2,
    },
    repository_state: baseSession.repository_state,
    review_mode: false,
  },
  step: {
    id: 2,
    command_text: 'git status',
    terminal_output: 'On branch main',
    result_category: 'TargetNotYetMatched',
    evaluation_result: 'TargetNotYetMatched',
    command_classification: 'non_counted_diagnostic',
    contextual_feedback: 'Nice diagnostic.',
    created_at: '2026-05-18T12:00:01Z',
  },
}

const completedResponse: CommandResponse = {
  session: {
    id: baseSession.id,
    mode: baseSession.mode,
    status: 'completed',
    difficulty_instance_id: baseSession.difficulty_instance_id,
    completed_at: baseSession.completed_at,
    first_attempt_star_eligible: baseSession.first_attempt_star_eligible,
    counts: baseSession.counts,
    repository_state: baseSession.repository_state,
    review_mode: false,
    mastery_progress: baseSession.mastery_progress,
    mastered_records: baseSession.mastered_records,
    completion: baseSession.completion,
    next_difficulty: baseSession.next_difficulty,
  },
  step: {
    id: 2,
    command_text: 'git status',
    terminal_output: 'On branch main',
    result_category: 'TargetMatched',
    evaluation_result: 'TargetMatched',
    command_classification: 'counted_action',
    contextual_feedback: 'Nice diagnostic.',
    created_at: '2026-05-18T12:00:01Z',
  },
}

function renderSubmissionHook(queryClient: QueryClient) {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
  return renderHook(() => useCommandSubmission(42, false), { wrapper })
}

describe('useCommandSubmission', () => {
  afterEach(() => {
    cleanup()
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('merges an in-progress command step without invalidating progress queries', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    queryClient.setQueryData(queryKeys.scenarioSession(42), {
      ...baseSession,
      status: 'started',
      steps: [
        {
          id: 1,
          command_text: 'git init',
          terminal_output: 'Initialized empty Git repository',
          result_category: 'TargetNotYetMatched',
          command_classification: 'counted_action',
          contextual_feedback: '',
          created_at: '2026-05-18T12:00:00Z',
        },
      ],
    })
    queryClient.setQueryData(queryKeys.modules, [])
    queryClient.setQueryData(queryKeys.dashboardSummary, {})
    vi.mocked(practiceApi.submitCommand).mockResolvedValue(startedResponse)
    const { result } = renderSubmissionHook(queryClient)

    await act(async () => {
      await result.current.mutateAsync('git status')
    })

    const updatedSession = queryClient.getQueryData<ScenarioSession>(queryKeys.scenarioSession(42))
    expect(updatedSession?.steps.map((step) => step.id)).toEqual([1, 2])
    expect(updatedSession?.counts.non_counted_diagnostic_total).toBe(1)
    expect(queryClient.getQueryState(queryKeys.modules)?.isInvalidated).toBe(false)
    expect(queryClient.getQueryState(queryKeys.dashboardSummary)?.isInvalidated).toBe(false)
  })

  it('invalidates progress queries after a command completes the session', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    queryClient.setQueryData(queryKeys.scenarioSession(42), {
      ...baseSession,
      status: 'started',
    })
    queryClient.setQueryData(queryKeys.modules, [])
    queryClient.setQueryData(queryKeys.dashboardSummary, {})
    vi.mocked(practiceApi.submitCommand).mockResolvedValue(completedResponse)
    const { result } = renderSubmissionHook(queryClient)

    await act(async () => {
      await result.current.mutateAsync('git status')
    })

    const updatedSession = queryClient.getQueryData<ScenarioSession>(queryKeys.scenarioSession(42))
    expect(updatedSession?.status).toBe('completed')
    await waitFor(() => {
      expect(queryClient.getQueryState(queryKeys.modules)?.isInvalidated).toBe(true)
      expect(queryClient.getQueryState(queryKeys.dashboardSummary)?.isInvalidated).toBe(true)
    })
  })
})
