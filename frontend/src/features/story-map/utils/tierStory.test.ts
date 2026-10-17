import { describe, expect, it } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

import { tierStoryContent } from './tierStory'

type StoryRun = Pick<TierRun, 'scenario_context' | 'variant' | 'tier'>

function run(scenario: Record<string, unknown>, label = 'Clone docs-portal'): StoryRun {
  return {
    scenario_context: { schema_version: 3, ...scenario },
    variant: { id: 1, label, changed_variant: false },
    tier: { adventure_level_title: 'Cloning Repositories' },
  } as unknown as StoryRun
}

describe('tierStoryContent', () => {
  it('moves the starting point from an older saved run into the task', () => {
    const content = tierStoryContent(run({
      task: 'Clone api-lab into api-workshop.',
      details: [{ label: '', value: 'Your internship starts Monday.\n\nStarting point: Outside any repository.' }],
    }))
    expect(content.intro).toBe('Your internship starts Monday.')
    expect(content.task).toBe('Clone api-lab into api-workshop.\n\nStarting point: Outside any repository.')
    expect(content.requiredValues).toEqual([])
  })

  it('does not duplicate a starting point already included in the task', () => {
    const task = 'Clone the repository.\n\nStarting point: Outside any repository.'
    const content = tierStoryContent(run({ story: 'Story.\n\nStarting point: Outside any repository.', task }))
    expect(content.intro).toBe('Story.')
    expect(content.task).toBe(task)
  })

  it('preserves the briefing from newly seeded runs', () => {
    const task = 'Clone the repository.\n\nStarting point: Outside any repository.'
    const content = tierStoryContent(run({ story: 'Story.', task }))
    expect(content.intro).toBe('Story.')
    expect(content.task).toBe(task)
  })

  it('uses the first unlabeled detail as the intro and keeps labeled details as required values', () => {
    const content = tierStoryContent(
      run({
        story: 'Clone with the requested destination.',
        real_world_context: 'A clone gives the contributor the shared project history.',
        task: 'Use the provided remote URL.',
        details: [
          { label: '', value: 'Your team portal is hosted remotely.' },
          { label: 'Repository URL', value: 'https://example.test/docs-portal.git' },
        ],
      }),
    )

    expect(content).toEqual({
      title: 'Clone docs-portal',
      intro: 'Your team portal is hosted remotely.',
      realWorldContext: 'A clone gives the contributor the shared project history.',
      task: 'Use the provided remote URL.',
      requiredValues: [{ label: 'Repository URL', value: 'https://example.test/docs-portal.git' }],
    })
  })

  it('falls back to the tier story and the level title when the variant data is missing', () => {
    const content = tierStoryContent(run({ story: 'Initialize the current folder.' }, '  '))

    expect(content.title).toBe('Cloning Repositories')
    expect(content.intro).toBe('Initialize the current folder.')
    expect(content.realWorldContext).toBe('')
    expect(content.task).toBe('')
    expect(content.requiredValues).toEqual([])
  })

  it('tolerates an empty scenario context', () => {
    const content = tierStoryContent(run({}))

    expect(content.intro).toBe('')
    expect(content.requiredValues).toEqual([])
  })
})
