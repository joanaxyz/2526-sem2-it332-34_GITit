import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiRequest: vi.fn().mockResolvedValue({}),
}))

import { apiRequest } from '@/shared/api/httpClient'
import { commandAdventuresApi } from './commandAdventuresApi'

const mockedApiRequest = vi.mocked(apiRequest)

describe('commandAdventuresApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('starts a run at the adventure-slug route', () => {
    commandAdventuresApi.startRun('repo-basecamp')
    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/command-adventures/repo-basecamp/runs/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('submits a command to the adventure-runs route', () => {
    commandAdventuresApi.submitCommand(7, 'git init')
    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/adventure-runs/7/submit-command/',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ command: 'git init' }) }),
    )
  })

  it('uses a hint at the use-hint route', () => {
    commandAdventuresApi.useHint(7)
    expect(mockedApiRequest).toHaveBeenCalledWith(
      '/adventure-runs/7/use-hint/',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
