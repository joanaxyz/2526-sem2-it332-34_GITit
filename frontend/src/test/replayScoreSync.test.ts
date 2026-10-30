import { QueryClient, QueryObserver } from '@tanstack/react-query'
import { waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import type { ChallengeCommandResponse, ChallengeRun } from '@/features/challenges/types'
import { subscribeToChallengeRunSync, syncChallengeRunInCache } from '@/features/challenges/utils/challengeRunCache'
import type { TierCommandResponse, TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import { subscribeToTierRunSync, syncTierRunInCache } from '@/features/story-map/utils/tierRunCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'
import { useOptimisticGitCommand } from '@/shared/level-runtime/useOptimisticGitCommand'

vi.mock('@/shared/level-runtime/useOptimisticGitCommand', () => ({ useOptimisticGitCommand: vi.fn() }))

class TestChannel extends EventTarget {
  static open = new Set<TestChannel>()
  static sent: unknown[] = []
  readonly name: string

  constructor(name: string) {
    super()
    this.name = name
    TestChannel.open.add(this)
  }

  postMessage(data: unknown) {
    TestChannel.sent.push(data)
    for (const peer of TestChannel.open) {
      if (peer !== this && peer.name === this.name) {
        peer.dispatchEvent(new MessageEvent('message', { data }))
      }
    }
  }

  close() { TestChannel.open.delete(this) }
}

// Both submission adapters share the scoring and command-response contract.
function startedRun(replay: boolean): ChallengeRun & TierRun {
  return {
    id: 42, replay, status: 'started', stars: 0, completed_at: null, failure_reason: null,
    difficulty: 'easy', reward_coins: 0, reward: { coins: 0, claimed: true },
    challenge: { id: 2, slug: 'repository-basics', title: 'Repository basics', summary: '', narrative: '', level_id: 3 },
    tier: { id: 2, difficulty: 'easy', adventure_level_id: 3, adventure_level_slug: 'repository-basics', adventure_level_title: 'Repository basics', adventure_level_number: 1 },
    chapter: { id: 1, number: 1, title: 'Foundations' }, story: null,
    variant: { id: 4, label: 'Stage README', changed_variant: false },
    scenario: { index: 1, total: 1, title: 'Stage README' }, scenario_context: {},
    progress: { completed: 1, total: 1, cleared: true, next_scenario: null },
    mastery_progress: { cleared: true, stars: 1 },
    policy: { scoring_policy_version: 2, min_counted_commands: 1, generous_counted_commands: 2, max_counted_commands: 3 },
    counts: { counted_action_total: 0, minimum_counted_commands: 1, maximum_counted_commands: 3, non_counted_diagnostic_total: 0, remaining_counted_commands: 3, max_reached: false, total_attempts: 0 },
    scaffolding: { live_dag: true, expected_state: false, contextual_feedback: false },
    repository_state: { commits: [], branches: { main: null }, head: { type: 'branch', name: 'main' }, staging: {}, working_tree: {}, conflicts: [] },
    visualization: { commit_dag: {} }, expected_state: null, steps: [], next_difficulty: null, sibling_levels: [],
    completion: { stars: 1, counted_action_total: 3, completed_at: '2026-10-29T00:00:00Z' },
    star_breakdown: { stars: 0, available_stars: 3, counted_commands: 0, command_target: 1, generous_target: 2, maximum_commands: 3, scoring_policy_version: 2, retry_count: 0, graded_under_previous_rules: false, criteria: [] },
    tutor: null, guide_elsewhere: null, command_guides: [], tips: [],
  }
}

function completedResponse(run: ChallengeRun & TierRun): ChallengeCommandResponse & TierCommandResponse {
  return {
    run: {
      ...run, status: 'completed', stars: 3, completed_at: '2026-10-30T00:00:00Z',
      counts: { ...run.counts, counted_action_total: 1, total_attempts: 1, remaining_counted_commands: 2 },
      completion: { stars: 3, counted_action_total: 1, completed_at: '2026-10-30T00:00:00Z' },
      star_breakdown: { ...run.star_breakdown, stars: 3, available_stars: 3, counted_commands: 1 },
    },
    step: { id: 7, command_text: 'git add README.md', terminal_output: '', command_classification: 'counted', contextual_feedback: '', result_category: 'target_matched', evaluation_result: 'target_matched', created_at: '2026-10-30T00:00:00Z', visualization_snapshot: { commit_dag: {} } },
    command_outcome: { processed: true, counted: true, solved: true, failed: false, command_family: 'add', previous_rules_passing: 0, rules_passing: 1, rules_delta: 1, total_rules: 1, max_counted_commands: 3, counted_command_count: 1, remaining_counted_commands: 2 },
    command_family: 'add', diagnostic_metadata: [], exit_code: 0, stdout: '', stderr: '',
  }
}

describe.each([
  { name: 'adventure', hook: useTierCommandSubmission, sync: syncTierRunInCache, subscribe: subscribeToTierRunSync, channel: 'git-it:adventure-tier-run-sync' },
  { name: 'challenge', hook: useChallengeCommandSubmission, sync: syncChallengeRunInCache, subscribe: subscribeToChallengeRunSync, channel: 'git-it:challenge-run-sync' },
])('$name score synchronization', (mode) => {
  const cleanups: (() => void)[] = []

  function client() {
    const result = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } })
    cleanups.push(() => result.clear())
    return result
  }

  function complete(playTab: QueryClient, run: ChallengeRun & TierRun) {
    mode.hook(run.id)
    const config = vi.mocked(useOptimisticGitCommand).mock.calls.at(-1)![0]
    config.onSuccess(completedResponse(run), run, playTab)
  }

  beforeEach(() => {
    vi.stubGlobal('BroadcastChannel', TestChannel)
    TestChannel.sent = []
    useAuthStore.setState({
      accessToken: 'test-token', user: { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false },
      sessionUserId: 1, sessionGeneration: 1,
    })
  })

  afterEach(() => {
    for (const cleanup of cleanups.splice(0).reverse()) cleanup()
    TestChannel.open.clear()
    vi.clearAllMocks()
    vi.unstubAllGlobals()
    useAuthStore.setState({ accessToken: null, user: null, sessionUserId: null, sessionGeneration: 0 })
    window.sessionStorage.clear()
    window.localStorage.clear()
  })

  it.each([false, true])('refreshes an already-open map and home after a clear (replay=%s)', async (replay) => {
    const playTab = client()
    const mapTab = client()
    cleanups.push(mode.subscribe(playTab), mode.subscribe(mapTab))
    let savedStars = 1
    const observers = [
      new QueryObserver(mapTab, { queryKey: queryKeys.chapterOverview(1), staleTime: Infinity, queryFn: async () => ({ savedStars }) }),
      new QueryObserver(mapTab, { queryKey: queryKeys.homeSummary, staleTime: 300_000, queryFn: async () => ({ savedStars }) }),
    ]
    mapTab.setQueryData(queryKeys.chapterOverview(1), { savedStars })
    mapTab.setQueryData(queryKeys.homeSummary, { savedStars })
    for (const observer of observers) cleanups.push(observer.subscribe(() => {}))

    const run = startedRun(replay)
    mode.sync(playTab, run)
    await waitFor(() => expect(observers.every((observer) => !observer.getCurrentResult().isFetching)).toBe(true))
    savedStars = 3
    TestChannel.sent = []
    complete(playTab, run)

    await waitFor(() => {
      for (const observer of observers) expect(observer.getCurrentResult().data).toEqual({ savedStars: 3 })
    })
    // Receiving tabs invalidate locally without sending another broadcast.
    expect(TestChannel.sent).toHaveLength(1)
  })

  it('keeps the saved score fresh on same-tab map return after a replay', async () => {
    const playTab = client()
    playTab.setQueryData(queryKeys.chapterOverview(1), { savedStars: 1 })
    const run = startedRun(true)
    mode.sync(playTab, run)
    complete(playTab, run)
    const observer = new QueryObserver(playTab, { queryKey: queryKeys.chapterOverview(1), staleTime: Infinity, queryFn: async () => ({ savedStars: 3 }) })
    cleanups.push(observer.subscribe(() => {}))
    await waitFor(() => expect(observer.getCurrentResult().data).toEqual({ savedStars: 3 }))
  })

  it.each(['started', 'failed', 'abandoned'] as const)('does not broadcast %s replays as progress', (status) => {
    mode.sync(client(), { ...startedRun(true), status })
    expect(TestChannel.sent).toEqual([])
    expect(window.localStorage.getItem(mode.channel)).toBeNull()
  })

  it('publishes completed replay scores through the storage fallback', () => {
    vi.stubGlobal('BroadcastChannel', undefined)
    const playTab = client()
    const run = startedRun(true)
    mode.sync(playTab, run)
    complete(playTab, run)
    expect(JSON.parse(window.localStorage.getItem(mode.channel)!)).toMatchObject({
      userId: 1, run: { id: run.id, replay: true, status: 'completed', completion: { stars: 3 } },
    })
  })
})
