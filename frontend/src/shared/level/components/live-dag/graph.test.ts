import { describe, expect, it } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
import { NO_DELTA } from './constants'
import { snapshotDelta } from './graph'

const baseSnapshot: RepositorySnapshot = {
  repository_initialized: true,
  commits: [{ id: 'c1', message: 'Base', parents: [], tree: {}, changes: {} }],
  branches: { main: 'c1', feature: 'c1' },
  head: { type: 'branch', name: 'main', target: 'c1' },
  staging: {},
  working_tree: {},
  conflicts: [],
  remotes: {},
  remote_branches: {},
  upstream_tracking: {},
  stash_stack: [],
  reflog: [],
  partial_hunks: {},
  operation_metadata: {},
}

describe('snapshotDelta', () => {
  it('identifies the commit, edge target, branch landing, and HEAD landing for a new commit', () => {
    const next: RepositorySnapshot = {
      ...baseSnapshot,
      commits: [
        ...baseSnapshot.commits,
        { id: 'c2', message: 'Next', parents: ['c1'], tree: {}, changes: {} },
      ],
      branches: { ...baseSnapshot.branches, main: 'c2' },
      head: { type: 'branch', name: 'main', target: 'c2' },
    }

    const delta = snapshotDelta(baseSnapshot, next)

    expect([...delta.commits]).toEqual(['c2'])
    expect(delta.refsByCommit.get('c2')).toEqual(['main'])
    expect(delta.headTarget).toBe('c2')
  })

  it('animates HEAD when checkout changes the active branch without changing topology', () => {
    const next: RepositorySnapshot = {
      ...baseSnapshot,
      head: { type: 'branch', name: 'feature', target: 'c1' },
    }

    const delta = snapshotDelta(baseSnapshot, next)

    expect(delta.commits.size).toBe(0)
    expect(delta.refsByCommit.size).toBe(0)
    expect(delta.headTarget).toBe('c1')
  })

  it('returns the stable empty delta when the repository state is unchanged', () => {
    expect(snapshotDelta(baseSnapshot, { ...baseSnapshot })).toBe(NO_DELTA)
  })
})
