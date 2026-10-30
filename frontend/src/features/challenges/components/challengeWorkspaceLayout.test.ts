import { describe, expect, it } from 'vitest'

import { mapUrlForRun } from './challengeWorkspaceLayout'

describe('challenge return navigation', () => {
  it('returns to the story and chapter attached to the run', () => {
    expect(mapUrlForRun({
      chapter: { id: 8, number: 2, title: 'Branching' },
      story: { id: 4, slug: 'another-story', title: 'Another Story', world_slug: 'arcane-spire' },
    })).toBe('/stories/another-story?chapter=8')
  })

  it('uses the current Arcane Spire destination when no story is provided', () => {
    expect(mapUrlForRun({
      chapter: { id: 35, number: 0, title: 'Orientation' },
      story: null,
    })).toBe('/stories/arcane-spire?chapter=35')
  })
})
