import { describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import { writeWorkspaceFile } from '@/shared/git/simulator/workspaceFiles'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import type { RepositoryValue } from '@/shared/level/types'

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

describe('revised scenario workflows', () => {
  it('finishes a merge after mergetool stages the saved result', () => {
    const initial = state({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'src/app.py': 'base' } },
        { id: 'c1', message: 'main', parents: ['c0'], tree: { 'src/app.py': 'ours' } },
        { id: 'c2', message: 'feature', parents: ['c0'], tree: { 'src/app.py': 'theirs' } },
      ],
      branches: { main: 'c1', 'feature/app': 'c2' },
      head: { type: 'branch', name: 'main', target: 'c1' },
    })

    const merged = executeGitCommand(initial, 'git merge feature/app')
    const opened = executeGitCommand(merged.next_state, 'git mergetool')
    const resolved = writeWorkspaceFile(opened.next_state, {
      path: 'src/app.py',
      content: 'resolved',
    })
    const committed = executeGitCommand(resolved, 'git commit --no-edit')

    expect(resolved.conflicts).toEqual([])
    expect(resolved.staging['src/app.py']).toMatchObject({ content: 'resolved' })
    expect(committed.processed).toBe(true)
    expect(committed.next_state.commits.at(-1)).toMatchObject({
      parents: ['c1', 'c2'],
      tree: { 'src/app.py': 'resolved' },
    })
  })

  it('stops a conflicting cherry-pick and continues after a manual resolution', () => {
    const initial = state({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'src/export.py': 'base' } },
        { id: 'c1', message: 'fix export', parents: ['c0'], tree: { 'src/export.py': 'fixed' } },
        { id: 'c2', message: 'main', parents: ['c1'], tree: { 'src/export.py': 'fixed', 'README.md': 'main' } },
        { id: 'c3', message: 'release', parents: ['c0'], tree: { 'src/export.py': 'release' } },
      ],
      branches: { main: 'c2', 'release-2.0': 'c3' },
      head: { type: 'branch', name: 'release-2.0', target: 'c3' },
      cherry_pick_conflict_files: ['src/export.py'],
    })

    const stopped = executeGitCommand(initial, 'git cherry-pick c1')
    const edited = writeWorkspaceFile(stopped.next_state, {
      path: 'src/export.py',
      content: 'fixed for release',
    })
    const staged = executeGitCommand(edited, 'git add src/export.py')
    const continued = executeGitCommand(staged.next_state, 'git cherry-pick --continue')

    expect(stopped.next_state.conflicts).toEqual(['src/export.py'])
    expect(continued.processed).toBe(true)
    expect(continued.next_state.cherry_pick_in_progress).toBeUndefined()
    expect(continued.next_state.commits.at(-1)).toMatchObject({
      message: 'fix export',
      parents: ['c3'],
      tree: { 'src/export.py': 'fixed for release' },
    })
  })

  it('records the source trailer for cherry-pick -x', () => {
    const initial = state({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { app: 'base' } },
        { id: 'c1', message: 'fix app', parents: ['c0'], tree: { app: 'fixed' } },
        { id: 'c2', message: 'release', parents: ['c0'], tree: { app: 'base' } },
      ],
      branches: { main: 'c1', release: 'c2' },
      head: { type: 'branch', name: 'release', target: 'c2' },
    })

    const result = executeGitCommand(initial, 'git cherry-pick -x c1')

    expect(result.next_state.commits.at(-1)?.message).toContain('(cherry picked from commit c1)')
  })

  it('continues a stopped rebase and replays the remaining commits', () => {
    const original = state({
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { limiter: 'base' } },
        { id: 'c1', message: 'main', parents: ['c0'], tree: { limiter: 'main' } },
        { id: 'c2', message: 'retry', parents: ['c0'], tree: { limiter: 'retry' } },
        { id: 'c3', message: 'docs', parents: ['c2'], tree: { limiter: 'retry', docs: 'limits' } },
      ],
      branches: { main: 'c1', feature: 'c3' },
      head: { type: 'branch', name: 'feature', target: 'c3' },
    })
    const stopped = state({
      ...original,
      branches: { main: 'c1', feature: 'c1' },
      head: { type: 'branch', name: 'feature', target: 'c1' },
      conflicts: ['limiter'],
      working_tree: { limiter: { status: 'conflicted', content: 'markers' } },
      rebase_state: {
        abort_state: original,
        branch: 'feature',
        current_source: 'c2',
        remaining: ['c3'],
        applied: [],
      } as unknown as RepositoryValue,
    })

    const edited = writeWorkspaceFile(stopped, { path: 'limiter', content: 'resolved' })
    const staged = executeGitCommand(edited, 'git add limiter')
    const continued = executeGitCommand(staged.next_state, 'git rebase --continue')

    expect(continued.processed).toBe(true)
    expect(continued.next_state.rebase_state).toBeUndefined()
    expect(continued.next_state.commits.at(-1)).toMatchObject({
      message: 'docs',
      tree: { limiter: 'resolved', docs: 'limits' },
    })
  })
})
