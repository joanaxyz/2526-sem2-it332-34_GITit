import { describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

function baseState(overrides: Partial<MutableRepositoryState> = {}): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [],
    branches: {},
    head: { type: 'branch', name: 'main' },
    staging: {},
    working_tree: {},
    conflicts: [],
    conflict_details: {},
    ...overrides,
  }
}

describe('executeGitCommand', () => {
  it('stages and commits worktree files in the browser', () => {
    const staged = executeGitCommand(
      baseState({
        working_tree: {
          'README.md': { status: 'untracked', content: 'hello' },
        },
      }),
      'git add README.md',
    )

    expect(staged.processed).toBe(true)
    expect(staged.output).toBe('')
    expect(staged.next_state.staging['README.md']).toEqual({ status: 'untracked', content: 'hello' })
    expect(staged.next_state.working_tree).toEqual({})

    const committed = executeGitCommand(staged.next_state, 'git commit -m "initial commit"')

    expect(committed.processed).toBe(true)
    expect(committed.command_family).toBe('commit')
    expect(committed.output).toBe('[main c0] initial commit')
    expect(committed.next_state.branches.main).toBe('c0')
    expect(committed.next_state.staging).toEqual({})
    expect(committed.next_state.commits[0]).toMatchObject({
      id: 'c0',
      message: 'initial commit',
      parents: [],
      tree: { 'README.md': 'hello' },
    })
  })

  it('git init keeps existing files as untracked work so they can be committed', () => {
    const initialized = executeGitCommand(
      {
        repository_initialized: false,
        commits: [],
        branches: {},
        head: { type: 'none' },
        staging: {},
        working_tree: { 'README.md': 'notes', 'src/app.py': "print('hi')\n" },
        conflicts: [],
        conflict_details: {},
      } as unknown as MutableRepositoryState,
      'git init',
    )

    expect(initialized.next_state.repository_initialized).toBe(true)
    // The pre-existing files must survive `git init` (real git only adds .git).
    expect(Object.keys(initialized.next_state.working_tree).sort()).toEqual([
      'README.md',
      'src/app.py',
    ])

    const staged = executeGitCommand(initialized.next_state, 'git add .')
    const committed = executeGitCommand(staged.next_state, 'git commit -m "Initial commit"')

    expect(committed.next_state.commits).toHaveLength(1)
    expect(committed.next_state.commits[0]).toMatchObject({
      parents: [],
      tree: { 'README.md': 'notes', 'src/app.py': "print('hi')\n" },
    })
    expect(committed.next_state.working_tree).toEqual({})
  })

  it('marks diagnostic commands without mutating repository state', () => {
    const state = baseState({
      commits: [
        {
          id: 'c0',
          message: 'base',
          parents: [],
          tree: { 'README.md': 'hello' },
        },
      ],
      branches: { main: 'c0' },
      head: { type: 'branch', name: 'main', target: 'c0' },
      working_tree: {
        'README.md': { status: 'modified', content: 'hello again' },
      },
    })

    const result = executeGitCommand(state, 'git status --short')

    expect(result.processed).toBe(true)
    expect(result.diagnostic).toBe(true)
    expect(result.diagnostic_metadata).toEqual(['inspected_status'])
    expect(result.output).toContain('README.md')
    expect(result.next_state.working_tree).toEqual(state.working_tree)
  })

  it('rejects non-git commands without changing state', () => {
    const state = baseState()
    const result = executeGitCommand(state, 'python cleanup.py')

    expect(result.processed).toBe(false)
    expect(result.exit_code).toBe(127)
    expect(result.output).toBe('python: command not found')
    expect(result.next_state.commits).toEqual([])
  })

  it('accepts cd as a diagnostic no-op without changing repository state', () => {
    const state = baseState({
      commits: [{ id: 'c0', message: 'base', parents: [], tree: { 'README.md': 'x' } }],
      branches: { main: 'c0' },
      head: { type: 'branch', name: 'main', target: 'c0' },
      working_tree: { 'README.md': { status: 'modified', content: 'y' } },
    })
    const result = executeGitCommand(state, 'cd project')

    expect(result.processed).toBe(true)
    expect(result.exit_code).toBe(0)
    expect(result.diagnostic).toBe(true)
    expect(result.command_family).toBe('cd')
    expect(result.next_state.commits.map((c) => c.id)).toEqual(['c0'])
    expect(result.next_state.branches).toEqual({ main: 'c0' })
    expect(Object.keys(result.next_state.working_tree)).toEqual(['README.md'])
  })

  it('accepts cd before a repository exists', () => {
    const result = executeGitCommand(
      {
        repository_initialized: false,
        commits: [],
        branches: {},
        head: { type: 'none' },
        staging: {},
        working_tree: {},
        conflicts: [],
        conflict_details: {},
      } as unknown as MutableRepositoryState,
      'cd new-folder',
    )

    expect(result.processed).toBe(true)
    expect(result.exit_code).toBe(0)
  })

  it('pull --rebase replays local-only commits on top of a diverged remote instead of dropping them', () => {
    const state = baseState({
      commits: [
        { id: 'c0', message: 'Initial', parents: [], tree: { 'README.md': 'base' } },
        {
          id: 'local1',
          message: 'Local work',
          parents: ['c0'],
          tree: { 'README.md': 'base', 'local.txt': 'mine' },
        },
        {
          id: 'remote1',
          message: 'Remote work',
          parents: ['c0'],
          tree: { 'README.md': 'base', 'remote.txt': 'theirs' },
        },
      ],
      branches: { main: 'local1' },
      remotes: { origin: 'https://example.test/team/app.git' },
      remote_branches: { 'origin/main': 'remote1' },
      upstream_tracking: { main: 'origin/main' },
    } as unknown as Partial<MutableRepositoryState>)

    const result = executeGitCommand(state, 'git pull --rebase')

    expect(result.processed).toBe(true)
    const newHeadId = result.next_state.branches.main
    expect(newHeadId).not.toBe('remote1')
    const newHead = result.next_state.commits.find((commit) => commit.id === newHeadId)
    expect(newHead?.parents).toEqual(['remote1'])
    expect(newHead?.tree).toEqual({ 'README.md': 'base', 'remote.txt': 'theirs', 'local.txt': 'mine' })
    expect(newHead?.message).toBe('Local work')
  })
})

describe('fast-forward merge workspace state', () => {
  it('moves the branch ref without leaving target-tree paths staged', () => {
    const state = baseState({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'README.md': 'base' } },
        {
          id: 'c1',
          message: 'feature',
          parents: ['c0'],
          tree: { 'README.md': 'base', 'src/feature.ts': 'ready' },
        },
      ],
      branches: { main: 'c0', feature: 'c1' },
      head: { type: 'branch', name: 'main', target: 'c0' },
    })

    const result = executeGitCommand(state, 'git merge feature')

    expect(result.processed).toBe(true)
    expect(result.next_state.branches.main).toBe('c1')
    expect(result.next_state.staging).toEqual({})
    expect(result.next_state.working_tree).toEqual({})
  })
})
