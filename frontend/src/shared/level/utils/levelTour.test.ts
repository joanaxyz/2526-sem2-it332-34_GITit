import { afterEach, describe, expect, it, vi } from 'vitest'

import { hasSeenLevelTour, levelTourStorageKey, markLevelTourSeen } from './levelTour'

describe('level tour storage', () => {
  afterEach(() => {
    window.localStorage.clear()
    vi.restoreAllMocks()
  })

  it('keeps Adventure and Challenge completion independent for each user', () => {
    markLevelTourSeen(7, 'adventure')

    expect(hasSeenLevelTour(7, 'adventure')).toBe(true)
    expect(hasSeenLevelTour(7, 'challenge')).toBe(false)
    expect(hasSeenLevelTour(8, 'adventure')).toBe(false)
    expect(levelTourStorageKey(7, 'adventure')).toBe(
      'git-it-practice-workspace-tour:v3:7:adventure',
    )
  })

  it('defaults existing call sites to the redesigned Challenge tour key', () => {
    markLevelTourSeen(11)

    expect(hasSeenLevelTour(11)).toBe(true)
    expect(hasSeenLevelTour(11, 'adventure')).toBe(false)
    expect(window.localStorage.getItem('git-it-practice-workspace-tour:v3:11:challenge')).toBe(
      'seen',
    )
  })

  it('shows the new scoring and completion guidance once to users of the previous tour', () => {
    window.localStorage.setItem('git-it-practice-workspace-tour:v2:7:adventure', 'seen')
    window.localStorage.setItem('git-it-practice-workspace-tour:v2:7:challenge', 'seen')

    expect(hasSeenLevelTour(7, 'adventure')).toBe(false)
    expect(hasSeenLevelTour(7, 'challenge')).toBe(false)
    markLevelTourSeen(7, 'challenge')
    expect(hasSeenLevelTour(7, 'challenge')).toBe(true)
    expect(hasSeenLevelTour(7, 'adventure')).toBe(false)
  })

  it('fails safely when browser storage reads are blocked', () => {
    vi.spyOn(localStorage, 'getItem').mockImplementation(() => {
      throw new DOMException('Blocked', 'SecurityError')
    })

    expect(hasSeenLevelTour(7)).toBe(true)
  })

  it('fails safely when browser storage writes are blocked', () => {
    vi.spyOn(localStorage, 'setItem').mockImplementation(() => {
      throw new DOMException('Blocked', 'SecurityError')
    })

    expect(() => markLevelTourSeen(7)).not.toThrow()
  })
})
