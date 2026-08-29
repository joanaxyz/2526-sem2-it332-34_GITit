import { describe, expect, it } from 'vitest'

import {
  createWorkspaceFile,
  deleteWorkspaceFile,
  renameWorkspaceFile,
  writeWorkspaceFile,
  WorkspaceFileError,
} from '@/shared/git/simulator/workspaceFiles'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

function baseState(overrides: Partial<MutableRepositoryState> = {}): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [
      {
        id: 'c0',
        message: 'base',
        parents: [],
        tree: { 'README.md': 'hello', 'src/app.ts': 'console.log("hi")' },
      },
    ],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c0' },
    staging: {},
    working_tree: {},
    conflicts: [],
    conflict_details: {},
    ...overrides,
  }
}

describe('workspace file state helpers', () => {
  it('creates new files as untracked worktree entries', () => {
    const nextState = createWorkspaceFile(baseState(), {
      path: 'src/new-app.ts',
      content: 'console.log("hi")',
    })

    expect(nextState.working_tree['src/new-app.ts']).toEqual({
      status: 'untracked',
      content: 'console.log("hi")',
    })
    expect(nextState.operation_metadata?.last_workspace_file_created).toBe('src/new-app.ts')
  })

  it('writes tracked files as modified worktree entries', () => {
    const nextState = writeWorkspaceFile(baseState(), {
      path: 'README.md',
      content: 'hello again',
    })

    expect(nextState.working_tree['README.md']).toEqual({
      status: 'modified',
      content: 'hello again',
    })
    expect(nextState.operation_metadata?.last_workspace_file_written).toBe('README.md')
  })

  it('rejects absolute paths', () => {
    expect(() => createWorkspaceFile(baseState(), { path: '/etc/passwd', content: '' })).toThrow(WorkspaceFileError)
  })

  it('deletes untracked files and marks tracked files deleted in the worktree', () => {
    const created = createWorkspaceFile(baseState(), {
      path: 'notes/todo.md',
      content: 'draft',
    })

    const nextState = deleteWorkspaceFile(deleteWorkspaceFile(created, { path: 'notes/todo.md' }), { path: 'README.md' })

    expect(nextState.working_tree['notes/todo.md']).toBeUndefined()
    expect(nextState.working_tree['README.md']).toBe('deleted')
    expect(nextState.operation_metadata?.last_workspace_file_deleted).toBe('README.md')
  })

  it('renames a folder by moving its files without selecting the editor target', () => {
    const edited = writeWorkspaceFile(baseState(), {
      path: 'src/app.ts',
      content: 'console.log("bye")',
    })

    const nextState = renameWorkspaceFile(edited, {
      path: 'src',
      newPath: 'lib',
    })

    expect(nextState.working_tree['src/app.ts']).toBe('deleted')
    expect(nextState.working_tree['lib/app.ts']).toEqual({
      status: 'untracked',
      content: 'console.log("bye")',
    })
    expect(nextState.operation_metadata?.last_workspace_file_renamed_from).toBe('src')
    expect(nextState.operation_metadata?.last_workspace_file_renamed_to).toBe('lib')
  })
})
