import { describe, expect, it } from 'vitest'

import { executeGitCommand, executeTerminalCommand } from '@/shared/git/simulator/engine'
import { writeWorkspaceFile } from '@/shared/git/simulator/workspaceFiles'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import type { RepositoryValue } from '@/shared/level/types'

// Shapes required by the scenarios in backend/curriculum/seed_data/source/wave_plan/.

function state(overrides: Partial<MutableRepositoryState>): MutableRepositoryState {
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

function run(start: MutableRepositoryState, commands: string[]) {
  let current = start
  const results = []
  for (const command of commands) {
    const result = executeGitCommand(current, command)
    results.push(result)
    current = result.next_state
  }
  return { state: current, results }
}

const base = { 'README.md': 'readme-v1', 'config/app.yml': 'app-v1' }

function remoteMain(overrides: Partial<MutableRepositoryState> = {}) {
  return state({
    commits: [
      { id: 'c1', message: 'Base', parents: [], tree: { ...base } },
      { id: 'c2', message: 'Local edit', parents: ['c1'], tree: { ...base, 'README.md': 'readme-local' } },
      { id: 'c3', message: 'Teammate edit', parents: ['c1'], tree: { ...base, 'README.md': 'readme-remote' } },
    ],
    branches: { main: 'c2' },
    head: { type: 'branch', name: 'main' },
    remotes: { origin: 'https://example.test/team/app.git' },
    remote_branches: { 'origin/main': 'c1' },
    upstream_tracking: { main: 'origin/main' },
    remote_updates: { 'origin/main': 'c3' },
    ...overrides,
  })
}

describe('wave plan scenario shapes', () => {
  it('rejects a plain push of rewritten history and accepts a lease or force (state-only grading)', () => {
    const rewritten = state({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { ...base } },
        { id: 'c2', message: 'Fix stuff', parents: ['c1'], tree: { ...base, 'src/client.py': 'retry' } },
        { id: 'c3', message: 'Add retry to API client', parents: ['c1'], tree: { ...base, 'src/client.py': 'retry' } },
      ],
      branches: { main: 'c1', 'feature/api-retry': 'c3' },
      head: { type: 'branch', name: 'feature/api-retry' },
      remotes: { origin: 'https://example.test/team/api.git' },
      remote_branches: { 'origin/feature/api-retry': 'c2' },
      upstream_tracking: { 'feature/api-retry': 'origin/feature/api-retry' },
    })
    expect(executeGitCommand(rewritten, 'git push origin feature/api-retry').processed).toBe(false)
    for (const push of ['git push --force-with-lease origin feature/api-retry', 'git push --force origin feature/api-retry']) {
      const result = executeGitCommand(rewritten, push)
      expect(result.processed).toBe(true)
      expect((result.next_state.remote_branches as Record<string, string>)['origin/feature/api-retry']).toBe('c3')
    }
    // A lease refuses once the server moved after the last fetch.
    const moved = { ...rewritten, remote_updates: { 'origin/feature/api-retry': 'c2b' } }
    expect(executeGitCommand(moved, 'git push --force-with-lease origin feature/api-retry').processed).toBe(false)
  })

  it('records where a repository was created, including from inside its folder (1.1)', () => {
    const workspace = state({
      repository_initialized: false,
      working_tree: { 'services/billing-api/app.py': { status: 'untracked', content: 'app' } } as unknown as MutableRepositoryState['working_tree'],
    })
    const named = executeTerminalCommand(workspace, 'git init -b trunk services/billing-api', { cwd: '' })
    expect(named.execution.next_state.repository_root).toBe('services/billing-api')
    const inside = executeTerminalCommand(workspace, 'git init -b trunk', { cwd: 'services/billing-api' })
    expect(inside.execution.next_state.repository_root).toBe('services/billing-api')
    const here = executeGitCommand(workspace, 'git init -b trunk')
    expect(here.next_state.repository_root).toBe('.')
  })

  it("records each switch in the HEAD reflog, as Git does (2.3 round trips)", () => {
    const feature = state({
      commits: [{ id: 'c1', message: 'Base', parents: [], tree: { ...base } }],
      branches: { main: 'c1', 'feature/payments': 'c1' },
      head: { type: 'branch', name: 'feature/payments' },
    })
    const { state: done } = run(feature, ['git switch main', 'git switch feature/payments'])
    expect(done.reflog?.map((entry) => entry.message)).toEqual([
      'checkout: moving from feature/payments to main',
      'checkout: moving from main to feature/payments',
    ])
  })

  it('stacks two --no-commit picks and commits them together (3.3 Medium)', () => {
    const release = state({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { ...base, 'src/login.py': 'l1', 'src/session.py': 's1' } },
        { id: 'c2', message: 'Login fix', parents: ['c1'], tree: { ...base, 'src/login.py': 'l2', 'src/session.py': 's1' } },
        { id: 'c3', message: 'Session fix', parents: ['c2'], tree: { ...base, 'src/login.py': 'l2', 'src/session.py': 's2' } },
      ],
      branches: { main: 'c3', 'release-1.2': 'c1' },
      head: { type: 'branch', name: 'release-1.2' },
    })
    const { state: done, results } = run(release, [
      'git cherry-pick --no-commit c2',
      'git cherry-pick --no-commit c3',
      'git commit -m "Backport login fixes"',
    ])
    expect(results.every((result) => result.processed)).toBe(true)
    const tip = done.commits.find((commit) => commit.id === done.branches['release-1.2'])
    expect(tip?.parents).toEqual(['c1'])
    expect(tip?.tree).toEqual({ ...base, 'src/login.py': 'l2', 'src/session.py': 's2' })
  })

  it('squashes a branch onto a main that moved on without undoing main (2.8, Module 2 gate)', () => {
    const moved = state({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { ...base } },
        { id: 'c2', message: 'Filters', parents: ['c1'], tree: { ...base, 'src/filters.js': 'filters' } },
        { id: 'c3', message: 'Changelog', parents: ['c1'], tree: { ...base, 'README.md': 'readme-v2' } },
      ],
      branches: { main: 'c3', 'feature/filters': 'c2' },
    })
    const { state: done, results } = run(moved, ['git merge --squash feature/filters', 'git commit -m "Add filters"'])
    expect(results.every((result) => result.processed)).toBe(true)
    const tip = done.commits.find((commit) => commit.id === done.branches.main)
    expect(tip?.parents).toEqual(['c3'])
    expect(tip?.tree).toEqual({ ...base, 'README.md': 'readme-v2', 'src/filters.js': 'filters' })
  })

  it('keeps pushed and deleted server branches through a later fetch (2.9 Hard capstone)', () => {
    const start = state({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { ...base } },
        { id: 'c2', message: 'Draft notes', parents: ['c1'], tree: { ...base, 'docs/notes.md': 'draft' } },
        { id: 'c3', message: 'Final notes', parents: ['c2'], tree: { ...base, 'docs/notes.md': 'final' } },
        { id: 'c4', message: 'Old banner', parents: ['c1'], tree: { ...base, 'banner.md': 'old' } },
      ],
      branches: { main: 'c1' },
      remotes: { origin: 'https://example.test/team/app.git' },
      remote_branches: { 'origin/main': 'c1', 'origin/feature/notes': 'c2', 'origin/feature/old-banner': 'c4' },
      remote_updates: { 'origin/feature/notes': 'c3' },
      remote_stale_branches: ['origin/feature/old-banner'],
      upstream_tracking: { main: 'origin/main' },
    })
    const { state: done, results } = run(start, [
      'git fetch origin',
      'git merge --no-ff origin/feature/notes',
      'git push origin main',
      'git push origin --delete feature/notes',
      'git fetch --prune origin',
    ])
    expect(results.every((result) => result.processed)).toBe(true)
    expect(done.remote_branches).toEqual({ 'origin/main': done.branches.main })
    expect(done.commits.find((commit) => commit.id === done.branches.main)?.tree?.['docs/notes.md']).toBe('final')
  })

  it('stops a pull on a content conflict, then resolves, commits and publishes (3.1 Medium)', () => {
    const pulled = executeGitCommand(remoteMain(), 'git pull origin main')
    expect(pulled.processed).toBe(true)
    expect(pulled.next_state.conflicts).toEqual(['README.md'])

    const resolved = writeWorkspaceFile(pulled.next_state, { path: 'README.md', content: 'readme-merged' })
    const { state: done, results } = run(resolved, [
      'git add README.md',
      'git commit --no-edit',
      'git push origin main',
    ])
    expect(results.every((result) => result.processed)).toBe(true)
    const tip = done.commits.at(-1)
    expect(tip?.parents).toEqual(['c2', 'c3'])
    expect(tip?.tree?.['README.md']).toBe('readme-merged')
    expect((done.remote_branches as Record<string, string>)['origin/main']).toBe(tip?.id)
  })

  it('refuses a pull that would overwrite uncommitted edits, and stash → pull → pop works (2.5 Hard)', () => {
    const dirty = remoteMain({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { ...base } },
        { id: 'c3', message: 'Teammate edit', parents: ['c1'], tree: { ...base, 'README.md': 'readme-remote' } },
      ],
      branches: { main: 'c1' },
      working_tree: { 'README.md': { status: 'modified', content: 'readme-wip' } } as unknown as MutableRepositoryState['working_tree'],
    })

    const refused = executeGitCommand(dirty, 'git pull origin main')
    expect(refused.processed).toBe(false)

    const { state: done, results } = run(dirty, ['git stash', 'git pull origin main', 'git stash pop'])
    expect(results.map((result) => result.processed)).toEqual([true, true, true])
    expect(done.branches.main).toBe('c3')
    expect(done.working_tree['README.md']).toMatchObject({ content: 'readme-wip' })
  })

  it('keeps both sides of a divergent merge that does not conflict', () => {
    const diverged = state({
      commits: [
        { id: 'c1', message: 'base', parents: [], tree: { 'README.md': 'r1' } },
        { id: 'c2', message: 'ours', parents: ['c1'], tree: { 'README.md': 'r1', 'src/auth.py': 'local' } },
        { id: 'c3', message: 'theirs', parents: ['c1'], tree: { 'README.md': 'r1', 'src/tests.py': 'remote' } },
      ],
      branches: { 'feature/auth': 'c2', other: 'c3' },
      head: { type: 'branch', name: 'feature/auth' },
    })
    const merged = executeGitCommand(diverged, 'git merge other')
    expect(merged.processed).toBe(true)
    expect(merged.next_state.commits.at(-1)?.tree).toEqual({
      'README.md': 'r1',
      'src/auth.py': 'local',
      'src/tests.py': 'remote',
    })
  })

  it('stages only incoming changes when a merge stops on a conflict', () => {
    const diverged = state({
      commits: [
        { id: 'c1', message: 'base', parents: [], tree: { 'app.py': 'base', 'docs.md': 'd1' } },
        { id: 'c2', message: 'ours', parents: ['c1'], tree: { 'app.py': 'ours', 'docs.md': 'd1', 'local.py': 'l' } },
        { id: 'c3', message: 'theirs', parents: ['c1'], tree: { 'app.py': 'theirs', 'docs.md': 'd2' } },
      ],
      branches: { main: 'c2', feature: 'c3' },
      head: { type: 'branch', name: 'main' },
    })
    const stopped = executeGitCommand(diverged, 'git merge feature')
    expect(stopped.next_state.conflicts).toEqual(['app.py'])
    expect(Object.keys(stopped.next_state.staging)).toEqual(['docs.md'])
    const resolved = writeWorkspaceFile(stopped.next_state, { path: 'app.py', content: 'both' })
    const { state: done } = run(resolved, ['git add app.py', 'git commit --no-edit'])
    expect(done.commits.at(-1)?.tree).toEqual({ 'app.py': 'both', 'docs.md': 'd2', 'local.py': 'l' })
  })

  it('initializes a folder that already has files, then stages and commits two of them (1.3 Medium)', () => {
    const fresh = state({
      repository_initialized: false,
      working_tree: {
        'index.html': { status: 'untracked', content: 'home' },
        'styles.css': { status: 'untracked', content: 'css' },
        'notes.txt': { status: 'untracked', content: 'private' },
      } as unknown as MutableRepositoryState['working_tree'],
    })
    const { state: done, results } = run(fresh, [
      'git init -b main',
      'git add index.html styles.css',
      'git commit -m "Initial portfolio"',
    ])
    expect(results.every((result) => result.processed)).toBe(true)
    expect(done.commits).toHaveLength(1)
    expect(Object.keys(done.commits[0].tree ?? {}).sort()).toEqual(['index.html', 'styles.css'])
    expect(done.working_tree['notes.txt']).toMatchObject({ status: 'untracked' })
  })

  it('splits one file into two commits with add -p, then add (1.4 Hard)', () => {
    const mixed = state({
      commits: [{ id: 'c1', message: 'Base', parents: [], tree: { 'src/api.py': 'api-v1' } }],
      branches: { main: 'c1' },
      working_tree: {
        'src/api.py': { status: 'modified', hunks: ['expiry-fix-hunk', 'logging-tidy-hunk'] },
      } as unknown as MutableRepositoryState['working_tree'],
      partial_hunks: {
        'src/api.py': { target_hunks: ['expiry-fix-hunk'], leftover_hunks: ['logging-tidy-hunk'] },
      },
    })
    const { state: done, results } = run(mixed, [
      'git add -p src/api.py',
      'git commit -m "Fix token expiry check"',
      'git add src/api.py',
      'git commit -m "Tidy API logging"',
    ])
    expect(results.map((result) => result.processed)).toEqual([true, true, true, true])
    const [first, second] = done.commits.slice(-2)
    expect(first.message).toBe('Fix token expiry check')
    expect(second.message).toBe('Tidy API logging')
    expect(first?.tree?.['src/api.py']).not.toEqual(second?.tree?.['src/api.py'])
    expect(done.working_tree['src/api.py']).toBeUndefined()
  })

  it('continues a stopped rebase, then republishes with --force-with-lease (4.3 Hard)', () => {
    const original = state({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'src/search.py': 'base' } },
        { id: 'c1', message: 'main', parents: ['c0'], tree: { 'src/search.py': 'main' } },
        { id: 'c2', message: 'search filters', parents: ['c0'], tree: { 'src/search.py': 'filters' } },
      ],
      branches: { main: 'c1', 'feature/search': 'c2' },
      head: { type: 'branch', name: 'feature/search', target: 'c2' },
      remotes: { origin: 'https://example.test/team/app.git' },
      remote_branches: { 'origin/feature/search': 'c2' },
      upstream_tracking: { 'feature/search': 'origin/feature/search' },
    })
    const stopped = state({
      ...original,
      branches: { main: 'c1', 'feature/search': 'c1' },
      head: { type: 'branch', name: 'feature/search', target: 'c1' },
      conflicts: ['src/search.py'],
      working_tree: { 'src/search.py': { status: 'conflicted', content: 'markers' } } as unknown as MutableRepositoryState['working_tree'],
      rebase_state: {
        abort_state: original as unknown as RepositoryValue,
        branch: 'feature/search',
        current_source: 'c2',
        remaining: [],
        applied: [],
      },
    })

    const edited = writeWorkspaceFile(stopped, { path: 'src/search.py', content: 'main+filters' })
    const { state: done, results } = run(edited, [
      'git add src/search.py',
      'git rebase --continue',
      'git push --force-with-lease origin feature/search',
    ])
    expect(results.map((result) => result.processed)).toEqual([true, true, true])
    const tip = done.branches['feature/search']
    expect((done.remote_branches as Record<string, string>)['origin/feature/search']).toBe(tip)
    expect(done.commits.find((commit) => commit.id === tip)?.parents).toEqual(['c1'])
  })

  it('bookmarks a lost commit without switching, then cherry-picks it onto main (4.1 Hard)', () => {
    const afterReset = state({
      commits: [
        { id: 'c1', message: 'Base', parents: [], tree: { 'src/auth.py': 'auth-v1' } },
        { id: 'c3', message: 'Experiment', parents: ['c1'], tree: { 'src/auth.py': 'auth-v1', 'lab.py': 'x' } },
        { id: 'c4', message: 'Auth fix', parents: ['c3'], tree: { 'src/auth.py': 'auth-fixed', 'lab.py': 'x' } },
      ],
      branches: { main: 'c1' },
      head: { type: 'branch', name: 'main', target: 'c1' },
    })
    const { state: done, results } = run(afterReset, ['git branch recovery/auth c4', 'git cherry-pick c4'])
    expect(results.map((result) => result.processed)).toEqual([true, true])
    expect(done.branches['recovery/auth']).toBe('c4')
    expect(done.head).toMatchObject({ name: 'main' })
    const tip = done.commits.find((commit) => commit.id === done.branches.main)
    expect(tip?.tree).toEqual({ 'src/auth.py': 'auth-fixed' })
  })

  it('amends the unpublished commit, reverts a published one, and pushes once (4.2 Hard)', () => {
    const shop = state({
      commits: [
        { id: 'c0', message: 'Initial shop', parents: [], tree: { 'checkout.py': 'v1' } },
        { id: 'c1', message: 'Add cart', parents: ['c0'], tree: { 'checkout.py': 'v1', 'cart.py': 'c1' } },
        { id: 'c2', message: 'Break checkout', parents: ['c1'], tree: { 'checkout.py': 'broken', 'cart.py': 'c1' } },
        { id: 'c3', message: 'Add search', parents: ['c2'], tree: { 'checkout.py': 'broken', 'cart.py': 'c1', 'search.py': 's1' } },
        { id: 'c4', message: 'wip', parents: ['c3'], tree: { 'checkout.py': 'broken', 'cart.py': 'c1', 'search.py': 's1', 'export.py': 'e1' } },
      ],
      branches: { main: 'c4' },
      head: { type: 'branch', name: 'main', target: 'c4' },
      remotes: { origin: 'https://example.test/team/shop.git' },
      remote_branches: { 'origin/main': 'c3' },
      upstream_tracking: { main: 'origin/main' },
    })
    const { state: done, results } = run(shop, [
      'git commit --amend -m "Add order export"',
      'git revert c2',
      'git push',
    ])
    expect(results.map((result) => result.processed)).toEqual([true, true, true])
    const tip = done.commits.find((commit) => commit.id === done.branches.main)
    expect(tip?.tree?.['checkout.py']).toBe('v1')
    expect((done.remote_branches as Record<string, string>)['origin/main']).toBe(done.branches.main)
  })

  it('keeps the -x origin note when a cherry-pick stops on a conflict and is continued (3.3 Medium gate)', () => {
    const release = state({
      commits: [
        { id: 'c0', message: 'Tax baseline', parents: [], tree: { 'src/tax.py': 'rate = base' } },
        { id: 'c1', message: 'Release tweak', parents: ['c0'], tree: { 'src/tax.py': 'rate = release' } },
        { id: 'c2', message: 'Round tax per line', parents: ['c0'], tree: { 'src/tax.py': 'rate = rounded' } },
      ],
      branches: { main: 'c2', 'release/2.1': 'c1' },
      head: { type: 'branch', name: 'release/2.1', target: 'c1' },
    })
    const stopped = executeGitCommand(release, 'git cherry-pick -x c2')
    expect(stopped.processed).toBe(true)
    expect(stopped.next_state.conflicts).toEqual(['src/tax.py'])

    const resolved = writeWorkspaceFile(stopped.next_state, { path: 'src/tax.py', content: 'rate = rounded release' })
    const { state: done, results } = run(resolved, ['git add src/tax.py', 'git cherry-pick --continue'])
    expect(results.every((result) => result.processed)).toBe(true)
    expect(done.commits.at(-1)?.message).toBe('Round tax per line\n\n(cherry picked from commit c2)')
    expect(done.cherry_pick_message).toBeUndefined()
  })
})

