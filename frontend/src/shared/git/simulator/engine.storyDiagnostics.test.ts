import { describe, expect, it } from 'vitest'
import { executeGitCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

const state: MutableRepositoryState = {
  repository_initialized: true,
  commits: [
    { id: 'c0', message: 'root', parents: [], tree: { 'src/app.ts': 'stable' } },
    { id: 'c1', message: 'regression', parents: ['c0'], tree: { 'src/app.ts': 'broken' } },
  ],
  branches: { main: 'c1' },
  head: { type: 'branch', name: 'main', target: 'c1' },
  staging: {},
  working_tree: {},
  conflicts: [],
  config: { 'user.name': 'Contributor A', 'core.autocrlf': 'input' },
  operation_metadata: {
    bisect_good: 'c0',
    bisect_bad: 'c1',
    first_bad_commit: 'c1',
    rerere_paths: ['src/app.ts'],
    worktrees: [
      { path: '/workspace/repository', commit: 'c1', branch: 'main' },
      { path: '/workspace/hotfix', commit: 'c0', branch: 'hotfix' },
    ],
    sparse_paths: ['src', 'docs'],
    submodules: [{ path: 'vendor/ui', commit: 'a1b2c3d', describe: 'heads/main' }],
  },
}

describe('advanced story diagnostic tranche', () => {
  it.each([
    ['git bisect run test-suite', 'c1 is the first bad commit'],
    ['git bisect log', '# first bad: [c1]'],
    ['git rerere status', 'src/app.ts'],
    ['git worktree list', '/workspace/hotfix'],
    ['git sparse-checkout list', 'docs'],
    ['git submodule status', 'vendor/ui'],
    ['git config --get user.name', 'Contributor A'],
  ])('executes %s without mutating repository state', (command, expected) => {
    const result = executeGitCommand(state, command)
    expect(result.processed).toBe(true)
    expect(result.diagnostic).toBe(true)
    expect(result.output).toContain(expected)
    expect(result.next_state).toEqual(expect.objectContaining({ branches: { main: 'c1' } }))
  })
})
