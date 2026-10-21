import { describe, expect, it } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
import { NO_DELTA } from './constants'
import { buildGraph, snapshotDelta } from './graph'

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

  it('flags git init so the hollow orb can burst into the HEAD orb', () => {
    const folder: RepositorySnapshot = {
      ...baseSnapshot,
      repository_initialized: false,
      commits: [],
      branches: {},
      head: { type: 'branch', name: 'main', target: null },
    }
    const initialized: RepositorySnapshot = { ...folder, repository_initialized: true, branches: { main: null } }

    expect(snapshotDelta(folder, initialized).repositoryInitialized).toBe(true)
    expect(snapshotDelta(initialized, { ...initialized })).toBe(NO_DELTA)
  })

  it('returns the stable empty delta when the repository state is unchanged', () => {
    expect(snapshotDelta(baseSnapshot, { ...baseSnapshot })).toBe(NO_DELTA)
  })

  it('marks connectors as length-normalised commit links', () => {
    const snapshot: RepositorySnapshot = {
      ...baseSnapshot,
      commits: [
        ...baseSnapshot.commits,
        { id: 'c2', message: 'Next', parents: ['c1'], tree: {}, changes: {} },
      ],
      branches: { main: 'c2' },
      head: { type: 'branch', name: 'main', target: 'c2' },
    }

    const { edges } = buildGraph(snapshot, 'cyan', 'vertical')

    expect(edges[0]?.className).toBe('dag-ley-edge')
    expect(edges[0]?.type).toBe('commitLink')
    expect(edges[0]?.style).toMatchObject({ strokeWidth: 2 })
  })
})
