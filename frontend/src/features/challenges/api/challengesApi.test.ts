import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { challengesApi } from './challengesApi'

const mockedApiOperationRequest = vi.mocked(apiOperationRequest)

describe('challengesApi', () => {
  afterEach(() => vi.clearAllMocks())

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
