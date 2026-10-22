import { describe, expect, it } from 'vitest'

import type { WorkspaceRun } from '@/shared/level/workspace/types'

import { workspaceObjectives } from './workspaceObjectives'

function run(status: WorkspaceRun['status'], task?: string) {
  return {
    status,
    scenario_context: { schema_version: 3, story: 'Story', ...(task === undefined ? {} : { task }) },
  } as Pick<WorkspaceRun, 'status' | 'scenario_context'>
}

function runWithObjectives(status: WorkspaceRun['status'], objectiveChecks: string[]) {
  return {
    status,
    scenario_context: {
      schema_version: 3,
      story: 'Story',
      task: 'Fallback task',
      objective_checks: objectiveChecks,
    },
  } as Pick<WorkspaceRun, 'status' | 'scenario_context'>
}

describe('workspaceObjectives', () => {
  it('keeps the starting position in the briefing rather than the objective checklist', () => {
    expect(workspaceObjectives(run('started', 'Clone the repository.\n\nStarting point: Outside any repository.'))).toEqual([
      { id: 'task', text: 'Clone the repository.', status: 'pending' },
    ])
  })

  it('turns the task into a single pending objective while the run is in progress', () => {
    expect(workspaceObjectives(run('started', '  Initialize the repository.  '))).toEqual([
      { id: 'task', text: 'Initialize the repository.', status: 'pending' },
    ])
  })

  it('marks the objective done once the run completes', () => {
    expect(workspaceObjectives(run('completed', 'Initialize the repository.'))[0].status).toBe('done')
  })

  it('keeps a failed run pending: nothing reports a broken objective yet', () => {
    expect(workspaceObjectives(run('failed', 'Initialize the repository.'))[0].status).toBe('pending')
  })

  it('returns no objectives when the run has no task', () => {
    expect(workspaceObjectives(run('started'))).toEqual([])
    expect(workspaceObjectives(run('started', '   '))).toEqual([])
  })

  it('uses every authored checklist item instead of the fallback task', () => {
    expect(workspaceObjectives(runWithObjectives('started', ['Create the branch.', 'Switch to it.']))).toEqual([
      { id: 'objective-1', text: 'Create the branch.', status: 'pending' },
      { id: 'objective-2', text: 'Switch to it.', status: 'pending' },
    ])
  })

  it('keeps a transition-era embedded starting point out of the fallback objective', () => {
    expect(
      workspaceObjectives(
        run('started', 'Clone the repository.\n\nStarting point: Outside any repository.'),
      ),
    ).toEqual([{ id: 'task', text: 'Clone the repository.', status: 'pending' }])
  })
})
