import { describe, expect, it } from 'vitest'

import { GIT_COMMAND_NAMES } from '@/shared/git/simulator/commandMetadata'
import { executeGitCommand } from '@/shared/git/simulator/engine'
import { normalizeState } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

function repo(overrides: Partial<MutableRepositoryState> = {}) {
  return normalizeState({
    commits: [{ id: 'c0', message: 'base', parents: [], tree: { 'tracked.txt': 'base' } }],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main' },
    ...overrides,
  })
}

describe('terminal errors and explicit help', () => {
  it.each([
    'git switch', 'git switch -c', 'git checkout -b', 'git config',
    'git config --get', 'git clone', 'git restore', 'git merge', 'git rebase',
    'git reset --hard -- file.txt', 'git revert', 'git cherry-pick',
    'git check-ignore', 'git rev-list', 'git bisect', 'git worktree',
    'git sparse-checkout', 'git submodule', 'git cat-file', 'git branch -m',
    'git remote add', 'git --global config',
  ])('%s reports an error without giving away command syntax', (command) => {
    const state = repo()
    const result = executeGitCommand(state, command)
    expect(result.exit_code).not.toBe(0)
    expect(result.stdout).toBe('')
    expect(result.stderr).toBe(result.output)
    expect(result.output).not.toMatch(/usage:|Use:|Chapter|curriculum|<[^>]+>/i)
    expect(result.next_state).toEqual(state)
  })

  it.each(GIT_COMMAND_NAMES)('git %s -h shows help without executing or inspecting the repository', (name) => {
    const state = repo({ repository_initialized: false })
    const result = executeGitCommand(state, `git ${name} -h`)
    expect(result.diagnostic).toBe(true)
    expect(result.exit_code).toBe(129)
    expect(result.stdout).toContain(`usage: git ${name}`)
    expect(result.stderr).toBe('')
    expect(result.next_state).toEqual(state)
    expect(result.diagnostic_metadata).toEqual([])
  })

  it('supports bare git and help topics', () => {
    expect(executeGitCommand(repo(), 'git').stdout).toContain('usage: git')
    expect(executeGitCommand(repo(), 'git help switch').stdout).toContain('usage: git switch')
    expect(executeGitCommand(repo(), 'git switch --help').stdout).toContain('usage: git switch')
    expect(executeGitCommand(repo(), 'git help frobnicate').exit_code).toBe(1)
  })

  it('does not mistake quoted message values or paths for help requests', () => {
    const state = repo({ staging: { 'new.txt': { status: 'added', content: 'new' } } })
    const committed = executeGitCommand(state, 'git commit -m "--help"')
    expect(committed.diagnostic).toBe(false)
    expect(committed.next_state.commits.at(-1)?.message).toBe('--help')
    const staged = executeGitCommand(repo({ working_tree: { '-h': 'text' } }), 'git add -- -h')
    expect(staged.diagnostic).toBe(false)
    expect(staged.output).toBe('')
    expect(staged.next_state.staging).toHaveProperty('-h')
  })

  it('keeps successful operations silent and config queries read only', () => {
    const state = repo({ config: { 'user.name': 'Learner' } })
    const remote = executeGitCommand(state, 'git remote add origin https://example.test/repo.git')
    expect(remote.output).toBe('')
    expect(executeGitCommand(state, 'git config user.name').stdout).toBe('Learner')
    expect(executeGitCommand(state, 'git config user.name').diagnostic).toBe(true)
    expect(executeGitCommand(state, 'git config missing.key').exit_code).toBe(1)
    expect(executeGitCommand(state, 'git add').exit_code).toBe(0)
    expect(executeGitCommand(state, 'git add').stderr).toBe('Nothing specified, nothing added.')
  })
})

describe('git status output', () => {
  const dirty = () => repo({
    staging: {
      'new.txt': { status: 'untracked', content: 'new' },
      'tracked.txt': { status: 'modified', content: 'staged' },
    },
    working_tree: {
      'tracked.txt': { status: 'modified', content: 'edited again' },
      'notes.txt': { status: 'untracked', content: 'notes' },
      'cache.log': { status: 'ignored', content: 'log' },
    },
  })

  it('combines index and worktree columns, with correct new and untracked codes', () => {
    expect(executeGitCommand(dirty(), 'git status --short').stdout).toBe('A  new.txt\nMM tracked.txt\n?? notes.txt')
    expect(executeGitCommand(dirty(), 'git status --ignored --porcelain').stdout).toBe('A  new.txt\nMM tracked.txt\n?? notes.txt\n!! cache.log')
  })

  it('separates staged, unstaged, untracked and ignored files without command hints', () => {
    const output = executeGitCommand(dirty(), 'git status').stdout
    expect(output).toContain('Changes to be committed:\n\tnew file:   new.txt\n\tmodified:   tracked.txt')
    expect(output).toContain('Changes not staged for commit:\n\tmodified:   tracked.txt')
    expect(output).toContain('Untracked files:\n\tnotes.txt')
    expect(output).not.toMatch(/cache.log|git add|git restore|usage:/)
  })

  it('reports conflicts once, unborn branches and clean working trees correctly', () => {
    expect(executeGitCommand(repo({ conflicts: ['tracked.txt'], working_tree: { 'tracked.txt': 'conflict' } }), 'git status --short').stdout).toBe('UU tracked.txt')
    expect(executeGitCommand(repo({ commits: [], branches: {} }), 'git status -sb').stdout).toBe('## No commits yet on main')
    expect(executeGitCommand(repo(), 'git status').stdout).toBe('On branch main\nnothing to commit, working tree clean')
  })
})
