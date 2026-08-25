import { describe, expect, it } from 'vitest'

import { snapshot, snapshotForCommand } from '@/shared/git/simulator/state/snapshot'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

function conflictState(): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [
      {
        id: 'c0',
        message: 'Base',
        parents: [],
        tree: { 'src/relay.conf': 'load=low' },
      },
    ],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c0' },
    staging: {},
    working_tree: {
      'src/relay.conf': {
        status: 'conflicted',
        content: '<<<<<<< HEAD\nload=high\n=======\nload=low\n>>>>>>> team/strict',
      },
    },
    conflicts: ['src/relay.conf'],
    conflict_details: {
      'src/relay.conf': {
        base: 'load=medium',
        ours: 'load=high',
        theirs: 'load=low',
      },
    },
    operation_metadata: { last_merge_branch: 'team/strict' },
    last_merge_branch: 'team/strict',
    squash_merge_staged: true,
    scenario_marker: { preserve: ['arbitrary', 'metadata'] },
    project_tree: { stale: 'derived' },
    visible_tree: { stale: 'derived' },
  }
}

describe('repository snapshots', () => {
  it('preserves canonical conflict and legacy metadata without derived trees', () => {
    const state = conflictState()

    const result = snapshotForCommand(state)
    const mutableResult = result as MutableRepositoryState

    expect(result).not.toHaveProperty('project_tree')
    expect(result).not.toHaveProperty('visible_tree')
    expect(result.conflict_details).toEqual(state.conflict_details)
    expect(mutableResult.last_merge_branch).toBe('team/strict')
    expect(mutableResult.squash_merge_staged).toBe(true)
    expect(mutableResult.scenario_marker).toEqual({ preserve: ['arbitrary', 'metadata'] })
  })

  it('returns a deep clone and only adds display trees to display snapshots', () => {
    const state = conflictState()

    const commandSnapshot = snapshotForCommand(state, true) as MutableRepositoryState
    const displaySnapshot = snapshot(state, true) as MutableRepositoryState

    expect(displaySnapshot.last_merge_branch).toBe('team/strict')
    expect(displaySnapshot.project_tree).toBeDefined()
    expect(displaySnapshot.visible_tree).toEqual(displaySnapshot.project_tree)

    ;(displaySnapshot.visible_tree as Record<string, { content: unknown }>)['src/relay.conf'].content = 'mutated'
    expect(displaySnapshot.project_tree?.['src/relay.conf']).not.toMatchObject({ content: 'mutated' })

    ;(commandSnapshot.operation_metadata as Record<string, unknown>).last_merge_branch = 'mutated'
    ;((commandSnapshot.scenario_marker as { preserve: string[] }).preserve).push('mutated')
    expect(state.operation_metadata).toEqual({ last_merge_branch: 'team/strict' })
    expect(state.scenario_marker).toEqual({ preserve: ['arbitrary', 'metadata'] })
  })
})
