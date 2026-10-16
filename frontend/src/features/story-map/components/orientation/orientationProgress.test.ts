import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  clearOrientationDraft,
  readOrientationDraft,
  writeOrientationDraft,
} from './orientationProgress'

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

describe('orientation draft progress', () => {
  it('restores only steps that still exist and clamps the active step', () => {
    writeOrientationDraft(7, 12, {
      completedStepIds: ['intro', 'removed', 'intro'],
      stepIndex: 99,
    })

    expect(readOrientationDraft(7, 12, ['intro', 'practice'])).toEqual({
      completedStepIds: ['intro'],
      stepIndex: 1,
    })
  })

  it('isolates drafts by player and lesson', () => {
    writeOrientationDraft(7, 12, { completedStepIds: ['intro'], stepIndex: 1 })

    expect(readOrientationDraft(8, 12, ['intro'])).toBeNull()
    expect(readOrientationDraft(7, 13, ['intro'])).toBeNull()
  })

  it('does not erase completed checkpoints written by another tab', () => {
    writeOrientationDraft(7, 12, { completedStepIds: ['practice'], stepIndex: 2 })
    writeOrientationDraft(7, 12, { completedStepIds: ['intro'], stepIndex: 1 })

    expect(readOrientationDraft(7, 12, ['intro', 'practice', 'finish'])).toEqual({
      completedStepIds: ['practice', 'intro'],
      stepIndex: 2,
    })
  })

  it('drops malformed drafts instead of blocking the lesson', () => {
    localStorage.setItem('git-it:orientation-progress:v1:7:12', '{bad json')

    expect(readOrientationDraft(7, 12, ['intro'])).toBeNull()
    expect(localStorage.getItem('git-it:orientation-progress:v1:7:12')).toBeNull()
  })

  it('clears a draft once the server has the completed topic', () => {
    writeOrientationDraft(7, 12, { completedStepIds: ['intro'], stepIndex: 0 })
    clearOrientationDraft(7, 12)

    expect(readOrientationDraft(7, 12, ['intro'])).toBeNull()
  })
})
