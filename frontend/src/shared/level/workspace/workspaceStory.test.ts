import { describe, expect, it } from 'vitest'

import type { WorkspaceRun } from '@/shared/level/workspace/types'

import { workspaceStoryContent } from './workspaceStory'

type StoryRun = Pick<WorkspaceRun, 'scenario_context' | 'variant'>

const LEVEL_TITLE = 'Cloning Repositories'

function run(scenario: Record<string, unknown>, label = 'Clone docs-portal'): StoryRun {
  return {
    scenario_context: { schema_version: 3, ...scenario },
    variant: { id: 1, label, changed_variant: false },
  } as unknown as StoryRun
}

describe('workspaceStoryContent', () => {
  it('promotes the starting point from an older saved narrative into its explicit field', () => {
    const content = workspaceStoryContent(
      run({
        task: 'Clone api-lab into api-workshop.',
        details: [
          {
            label: '',
            value: 'Your internship starts Monday.\n\nStarting point: Outside any repository.',
          },
        ],
      }),
      LEVEL_TITLE,
    )

    expect(content.intro).toBe('Your internship starts Monday.')
    expect(content.startingPoint).toBe('Outside any repository.')
    expect(content.task).toBe('Clone api-lab into api-workshop.')
  })

  it('promotes a starting point embedded in a transition-era task without duplicating it', () => {
    const content = workspaceStoryContent(
      run({
        story: 'A clean story.',
        task: 'Clone the repository.\n\nStarting point: Outside any repository.',
      }),
      LEVEL_TITLE,
    )

    expect(content.intro).toBe('A clean story.')
    expect(content.startingPoint).toBe('Outside any repository.')
    expect(content.task).toBe('Clone the repository.')
  })

  it('uses the first unlabeled detail as the intro and keeps labeled details as required values', () => {
    const content = workspaceStoryContent(
      run({
        story: 'Clone with the requested destination.',
        starting_point: 'No local repository exists yet.',
        real_world_context: 'A clone gives the contributor the shared project history.',
        task: 'Use the provided remote URL.',
        expected_result: 'A local clone is ready for work.',
        details: [
          { label: '', value: 'Your team portal is hosted remotely.' },
          { label: 'Repository URL', value: 'https://example.test/docs-portal.git' },
        ],
      }),
      LEVEL_TITLE,
    )

    expect(content).toEqual({
      title: 'Clone docs-portal',
      intro: 'Your team portal is hosted remotely.',
      startingPoint: 'No local repository exists yet.',
      realWorldContext: 'A clone gives the contributor the shared project history.',
      task: 'Use the provided remote URL.',
      expectedResult: 'A local clone is ready for work.',
      requiredValues: [{ label: 'Repository URL', value: 'https://example.test/docs-portal.git' }],
    })
  })

  it('falls back to the scenario story and the level title when the variant data is missing', () => {
    const content = workspaceStoryContent(run({ story: 'Initialize the current folder.' }, '  '), LEVEL_TITLE)

    expect(content.title).toBe('Cloning Repositories')
    expect(content.intro).toBe('Initialize the current folder.')
    expect(content.realWorldContext).toBe('')
    expect(content.task).toBe('')
    expect(content.startingPoint).toBe('')
    expect(content.expectedResult).toBe('')
    expect(content.requiredValues).toEqual([])
  })

  it('tolerates an empty scenario context', () => {
    const content = workspaceStoryContent(run({}), LEVEL_TITLE)

    expect(content.intro).toBe('')
    expect(content.requiredValues).toEqual([])
  })
})
