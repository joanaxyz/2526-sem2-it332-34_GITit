import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { challengesApi } from './challengesApi'

const mockedApiOperationRequest = vi.mocked(apiOperationRequest)

describe('challengesApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('loads chapter content with explicit section query params', () => {
    challengesApi.chapterContent(4, 'challenges', { cursor: 12, limit: 6 })

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'chapters_content_retrieve',
      '/chapters/4/content/?section=challenges&cursor=12&limit=6',
    )
  })

  it('starts challenge runs through the generated contract helper', () => {
    challengesApi.startChallengeRun(99, { prior_run_id: 7, replay: true })

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_trials_runs_create',
      '/challenge-trials/99/runs/',
      { body: { source_entry_point: 'level_page', prior_run_id: 7, replay: true } },
    )
  })

  it('discards runs without allowing callers to override the generated method', () => {
    challengesApi.discardChallengeRun(11, { signal: new AbortController().signal })

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_destroy',
      '/challenge-runs/11/',
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    )
  })
})
