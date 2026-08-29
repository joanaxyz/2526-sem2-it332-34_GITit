import { afterEach, describe, expect, it, vi } from 'vitest'

import { hasSeenLevelTour, markLevelTourSeen } from './levelTour'

describe('level tour storage', () => {
  afterEach(() => {
    vi.restoreAllMocks()
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
