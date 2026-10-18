import { describe, expect, it } from 'vitest'

import { normalizeLevelContext } from '@/shared/level/utils/levelContext'

describe('normalizeLevelContext', () => {
  it('keeps a copyable value when its field label is intentionally hidden', () => {
    expect(
      normalizeLevelContext({
        story: 'Use the required commit message shown below.',
        details: [{ label: '', value: 'Save staged work' }],
      }).details,
    ).toEqual([{ label: '', value: 'Save staged work' }])
  })

  it('normalizes real-world context for the tier story modal', () => {
    expect(
      normalizeLevelContext({ real_world_context: '  Teams clone shared work locally.  ' })
        .realWorldContext,
    ).toBe('Teams clone shared work locally.')
  })

  it('normalizes the authored briefing fields and objective checklist', () => {
    const context = normalizeLevelContext({
      starting_point: '  On main with a clean worktree. ',
      objective_checks: ['  Create the branch. ', '', 'Switch to it.'],
      expected_result: '  The new branch is checked out. ',
    })

    expect(context.startingPoint).toBe('On main with a clean worktree.')
    expect(context.objectiveChecks).toEqual(['Create the branch.', 'Switch to it.'])
    expect(context.expectedResult).toBe('The new branch is checked out.')
  })
})
