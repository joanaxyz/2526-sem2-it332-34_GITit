import { describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

const state: MutableRepositoryState = {
  repository_initialized: true,
  commits: [
    {
      id: 'c0',
      message: 'Initial project',
      parents: [],
      author: 'Contributor A',
      tree: { 'README.md': 'hello world\nGit history' },
    },
    {
      id: 'c1',
      message: 'Add application',
      parents: ['c0'],
      author: 'Contributor B',
      tree: {
        'README.md': 'hello world\nGit history',
        'src/app.ts': 'export const app = true',
      },
    },
  ],
  branches: { main: 'c1', release: 'c0' },
  head: { type: 'branch', name: 'main', target: 'c1' },
  staging: {},
  working_tree: {},
  conflicts: [],
  tags: { 'v1.0.0': { target: 'c0', annotated: true } },
  remote_branches: { 'origin/main': 'c1' },
  operation_metadata: {
    signatures: {
      c1: { signer: 'Release Bot' },
      'v1.0.0': { signer: 'Release Bot' },
    },
  },
}

function run(command: string) {
  const result = executeGitCommand(state, command)
  expect(result.processed).toBe(true)
  expect(result.diagnostic).toBe(true)
  expect(result.next_state).toEqual(expect.objectContaining({ branches: state.branches }))
  return result
}

describe('advanced diagnostic command tranche', () => {
  it('resolves revisions and describes history from tags', () => {
    expect(run('git rev-parse HEAD').stdout).toBe('c1')
    expect(run('git rev-parse --show-toplevel').stdout).toBe('/workspace/repository')
    expect(run('git describe --tags').stdout).toBe('v1.0.0-1-gc1')
  })

  it('supports history summaries and repository forensics', () => {
    expect(run('git shortlog -sn').stdout).toContain('Contributor A')
    expect(run('git blame README.md').stdout).toContain('hello world')
    expect(run('git grep app HEAD').stdout).toContain('src/app.ts:export const app = true')
  })

  it('supports virtual integration and patch-series inspection', () => {
    expect(run('git merge-tree release main').stdout).toContain('base c0')
    expect(run('git range-diff c0..main c0..main').stdout).toContain('=')
  })

  it('supports signature, integrity, and object inspection', () => {
    expect(run('git verify-commit c1').stdout).toContain('Release Bot')
    expect(run('git verify-tag v1.0.0').stdout).toContain('verified')
    expect(run('git fsck --full').stdout).toContain('Checking objects')
    expect(run('git count-objects -vH').stdout).toContain('count:')
    expect(run('git cat-file -t c1').stdout).toBe('commit')
    expect(run('git ls-tree HEAD').stdout).toContain('src/app.ts')
  })

  it('supports ref plumbing inspection without mutation', () => {
    expect(run('git show-ref').stdout).toContain('refs/heads/main')
    expect(run('git for-each-ref').stdout).toContain('refs/tags/v1.0.0')
    expect(run('git symbolic-ref HEAD').stdout).toBe('refs/heads/main')
  })
})
