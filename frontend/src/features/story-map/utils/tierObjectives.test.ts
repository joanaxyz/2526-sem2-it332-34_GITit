import { describe, expect, it } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

import { tierObjectives } from './tierObjectives'

function run(status: TierRun['status'], task?: string) {
  return {
    status,
    scenario_context: { schema_version: 3, story: 'Story', ...(task === undefined ? {} : { task }) },
  } as Pick<TierRun, 'status' | 'scenario_context'>
}

function runWithObjectives(status: TierRun['status'], objectiveChecks: string[]) {
  return {
    status,
    scenario_context: {
      schema_version: 3,
      story: 'Story',
      task: 'Fallback task',
      objective_checks: objectiveChecks,
    },
  } as Pick<TierRun, 'status' | 'scenario_context'>
}

describe('tierObjectives', () => {
  it('keeps the starting position in the briefing rather than the objective checklist', () => {
    expect(tierObjectives(run('started', 'Clone the repository.\n\nStarting point: Outside any repository.'))).toEqual([
      { id: 'task', text: 'Clone the repository.', status: 'pending' },
    ])
  })

  it('turns the task into a single pending objective while the run is in progress', () => {
    expect(tierObjectives(run('started', '  Initialize the repository.  '))).toEqual([
      { id: 'task', text: 'Initialize the repository.', status: 'pending' },
    ])
  })

  it('marks the objective done once the run completes', () => {
    expect(tierObjectives(run('completed', 'Initialize the repository.'))[0].status).toBe('done')
  })

  it('keeps a failed run pending: nothing reports a broken objective yet', () => {
    expect(tierObjectives(run('failed', 'Initialize the repository.'))[0].status).toBe('pending')
  })

  it('returns no objectives when the run has no task', () => {
    expect(tierObjectives(run('started'))).toEqual([])
    expect(tierObjectives(run('started', '   '))).toEqual([])
  })

  it('uses every authored checklist item instead of the fallback task', () => {
    expect(tierObjectives(runWithObjectives('started', ['Create the branch.', 'Switch to it.']))).toEqual([
      { id: 'objective-1', text: 'Create the branch.', status: 'pending' },
      { id: 'objective-2', text: 'Switch to it.', status: 'pending' },
    ])
  })

  it('keeps a transition-era embedded starting point out of the fallback objective', () => {
    expect(
      tierObjectives(
        run('started', 'Clone the repository.\n\nStarting point: Outside any repository.'),
      ),
    ).toEqual([{ id: 'task', text: 'Clone the repository.', status: 'pending' }])
  })
})
