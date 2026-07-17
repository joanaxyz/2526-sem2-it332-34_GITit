import { describe, expect, it } from 'vitest'

import type { AdventureLevelSummary } from '@/features/story-map/types'
import { adventureLevelCleared, nextPlayableLevelId } from '@/features/story-map/utils/storyMapChapter'

function level(overrides: Partial<AdventureLevelSummary>): AdventureLevelSummary {
  return {
    item_type: 'adventure',
    id: 1,
    slug: 'level-1',
    title: 'Level 1',
    command: 'git status',
    locked: false,
    lock_reason: '',
    completion: null,
    is_passed: false,
    ...overrides,
  }
}

describe('story map chapter utilities', () => {
  it('treats passed adventure levels as cleared even without a completion payload', () => {
    expect(adventureLevelCleared(level({ is_passed: true }))).toBe(true)
  })

  it('selects the first unpassed unlocked level as the next playable node', () => {
    const levels = [
      level({ id: 1, is_passed: true }),
      level({ id: 2, is_passed: false }),
      level({ id: 3, is_passed: false }),
    ]

    expect(nextPlayableLevelId(levels, false)).toBe(2)
  })

  it('does not expose a playable node when the chapter is locked', () => {
    expect(nextPlayableLevelId([level({ id: 1 })], true)).toBeNull()
  })
})
