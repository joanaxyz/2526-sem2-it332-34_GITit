import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { adventuresApi } from './adventuresApi'

const mockedApiOperationRequest = vi.mocked(apiOperationRequest)

describe('adventuresApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('starts a run at the adventure-level route through the generated contract helper', () => {
    adventuresApi.startRun(42)
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_levels_runs_create',
      '/adventure-levels/42/runs/',
    )
  })

  it('submits a command to the adventure-runs route through the generated contract helper', () => {
    const execution = {
      processed: true,
      next_state: {
        commits: [],
        branches: {},
        head: { type: 'branch' as const, name: 'main' },
        staging: {},
        working_tree: {},
        conflicts: [],
      },
      output: '',
      normalized_command: 'git init',
      exit_code: 0,
      diagnostic: false,
      stdout: '',
      stderr: '',
      command_family: 'init',
      diagnostic_metadata: [],
    }
    adventuresApi.submitCommand(7, 'git init', execution)
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_runs_submit_command_create',
      '/adventure-runs/7/submit-command/',
      { body: { command: 'git init', execution } },
    )
  })

  it('uses generated operation ids for workspace file mutations', () => {
    const input = { path: 'README.md', content: 'hello' }

    adventuresApi.createFile(9, input)
    adventuresApi.writeFile(9, input)

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_runs_files_create',
      '/adventure-runs/9/files/',
      { body: input },
    )
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_runs_files_partial_update',
      '/adventure-runs/9/files/',
      { body: input },
    )
  })

  it('renames and deletes workspace files through direct file resource requests', () => {
    adventuresApi.renameFile(9, { path: 'src/app.ts', newPath: 'src/main.ts' })
    adventuresApi.deleteFile(9, 'src/main.ts')

    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_runs_files_update',
      '/adventure-runs/9/files/',
      { body: { path: 'src/app.ts', new_path: 'src/main.ts' } },
    )
    expect(mockedApiOperationRequest).toHaveBeenCalledWith(
      'adventure_runs_files_destroy',
      '/adventure-runs/9/files/?path=src%2Fmain.ts',
    )
  })
})
