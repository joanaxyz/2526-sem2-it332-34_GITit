import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { challengeRunsApi } from './challengeRunsApi'

const mockedApiOperationRequest = vi.mocked(apiOperationRequest)

const repositoryState = {
  commits: [],
  branches: {},
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

describe('challengeRunsApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('submits commands through the generated contract helper', () => {
    const execution = {
      processed: true,
      next_state: repositoryState,
      output: '',
      normalized_command: 'git init',
      exit_code: 0,
      diagnostic: false,
      stdout: '',
      stderr: '',
      command_family: 'init',
      diagnostic_metadata: [],
    }

    challengeRunsApi.submitCommand(5, 'git init', execution)

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_submit_command_create',
      '/challenge-runs/5/submit-command/',
      { body: { command: 'git init', execution } },
    )
  })

  it('uses generated operation ids for workspace file mutations', () => {
    const input = { path: 'README.md', content: 'hello' }

    challengeRunsApi.createFile(3, input)
    challengeRunsApi.writeFile(3, input)

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_files_create',
      '/challenge-runs/3/files/',
      { body: input },
    )
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_files_partial_update',
      '/challenge-runs/3/files/',
      { body: input },
    )
  })

  it('renames and deletes workspace files through direct file resource requests', () => {
    challengeRunsApi.renameFile(3, { path: 'src/app.ts', newPath: 'src/main.ts' })
    challengeRunsApi.deleteFile(3, 'src/main.ts')

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_files_update',
      '/challenge-runs/3/files/',
      { body: { path: 'src/app.ts', new_path: 'src/main.ts' } },
    )
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'challenge_runs_files_destroy',
      '/challenge-runs/3/files/?path=src%2Fmain.ts',
    )
  })
})
