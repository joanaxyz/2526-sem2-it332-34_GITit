import { describe, expect, it } from 'vitest'

import {
  createWorkspaceDirectory,
  createWorkspaceFile,
  deleteWorkspaceFile,
  renameWorkspaceFile,
  writeWorkspaceFile,
  WorkspaceFileError,
} from '@/shared/git/simulator/workspaceFiles'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { directoryEntries, pathKind } from '@/shared/git/simulator/workspaceTree'

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

  it('creates a real empty folder instead of a placeholder file', () => {
    const nextState = createWorkspaceFile(baseState(), { path: 'docs/', content: '' })

    expect(nextState.directories).toEqual(['docs'])
    expect(nextState.working_tree).toEqual({})
    expect(pathKind(nextState, 'docs')).toBe('directory')
    expect(directoryEntries(nextState, 'docs')).toEqual([])
  })

  it('drops the folder from the empty-folder list once it holds a file', () => {
    const folder = createWorkspaceDirectory(baseState(), { path: 'docs/guides' })
    const withFile = createWorkspaceFile(folder, { path: 'docs/guides/intro.md', content: '' })

    expect(withFile.directories).toBeUndefined()
    expect(pathKind(withFile, 'docs/guides')).toBe('directory')
  })

  it('keeps a folder on disk after its last file is deleted', () => {
    const nextState = deleteWorkspaceFile(baseState(), { path: 'src/app.ts' })

    expect(nextState.working_tree['src/app.ts']).toBe('deleted')
    expect(nextState.directories).toEqual(['src'])
    expect(pathKind(nextState, 'src')).toBe('directory')
    expect(directoryEntries(nextState, 'src')).toEqual([])
  })

  it('removes a deleted folder completely, including empty subfolders', () => {
    const nested = createWorkspaceDirectory(baseState(), { path: 'src/empty' })
    const nextState = deleteWorkspaceFile(nested, { path: 'src' })

    expect(pathKind(nextState, 'src')).toBeNull()
    expect(nextState.directories).toBeUndefined()
    expect(directoryEntries(nextState, '').map((entry) => entry.name)).toEqual(['README.md'])
  })

  it('recreates a deleted tracked file as a modification', () => {
    const deleted = deleteWorkspaceFile(baseState(), { path: 'README.md' })
    const recreated = createWorkspaceFile(deleted, { path: 'README.md', content: 'fresh' })

    expect(recreated.working_tree['README.md']).toEqual({ status: 'modified', content: 'fresh' })
  })

  it('renames a folder that still contains a deleted tracked file', () => {
    const state = baseState({
      commits: [
        {
          id: 'c0',
          message: 'base',
          parents: [],
          tree: { 'src/app.ts': 'app', 'src/old.ts': 'old' },
        },
      ],
    })
    const deleted = deleteWorkspaceFile(state, { path: 'src/old.ts' })
    const renamed = renameWorkspaceFile(deleted, { path: 'src', newPath: 'lib' })

    expect(renamed.working_tree['lib/app.ts']).toEqual({ status: 'untracked', content: 'app' })
    expect(renamed.working_tree['lib/old.ts']).toBeUndefined()
    expect(pathKind(renamed, 'src')).toBeNull()
  })

  it('moves empty subfolders along with a renamed folder', () => {
    const nested = createWorkspaceDirectory(baseState(), { path: 'src/empty' })
    const renamed = renameWorkspaceFile(nested, { path: 'src', newPath: 'lib' })

    expect(renamed.directories).toEqual(['lib/empty'])
    expect(pathKind(renamed, 'src')).toBeNull()
  })

  it('refuses to rename onto an existing folder', () => {
    const folder = createWorkspaceDirectory(baseState(), { path: 'lib' })

    expect(() => renameWorkspaceFile(folder, { path: 'src', newPath: 'lib' })).toThrow('lib is already a folder.')
  })
})
