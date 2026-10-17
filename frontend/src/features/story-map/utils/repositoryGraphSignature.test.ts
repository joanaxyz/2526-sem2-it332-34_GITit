import { describe, expect, it } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'

import { repositoryGraphSignature } from './repositoryGraphSignature'

const base = {
  repository_initialized: true,
  commits: [{ id: 'c1', message: 'Base', parents: [], tree: { 'a.txt': 'v1' } }],
  branches: { main: 'c1' },
  head: { type: 'branch', name: 'main', target: 'c1' },
  staging: {},
  working_tree: {},
  conflicts: [],
} as unknown as RepositorySnapshot

describe('repositoryGraphSignature', () => {
  it('changes with what the graph draws', () => {
    const signature = repositoryGraphSignature(base)

    expect(repositoryGraphSignature({ ...base, repository_initialized: false })).not.toBe(signature)
    expect(repositoryGraphSignature({ ...base, branches: { main: 'c1', feature: 'c1' } })).not.toBe(signature)
    expect(repositoryGraphSignature({ ...base, head: { type: 'detached', target: 'c1' } })).not.toBe(signature)
    expect(repositoryGraphSignature({ ...base, remote_branches: { 'origin/main': 'c1' } })).not.toBe(signature)
  })

  it('ignores working-tree and staging edits', () => {
    expect(
      repositoryGraphSignature({ ...base, working_tree: { 'a.txt': 'v2' }, staging: { 'a.txt': 'v2' } }),
    ).toBe(repositoryGraphSignature(base))
  })
})
