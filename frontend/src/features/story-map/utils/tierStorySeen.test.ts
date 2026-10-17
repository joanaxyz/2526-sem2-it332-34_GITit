import { afterEach, describe, expect, it, vi } from 'vitest'

import { hasSeenTierStory, markTierStorySeen } from './tierStorySeen'

describe('tier story seen flag', () => {
  afterEach(() => {
    window.localStorage.clear()
    vi.restoreAllMocks()
  })

  it('is kept per user, adventure level and difficulty', () => {
    markTierStorySeen(7, 12, 'easy')

    expect(hasSeenTierStory(7, 12, 'easy')).toBe(true)
    expect(hasSeenTierStory(7, 12, 'medium')).toBe(false)
    expect(hasSeenTierStory(7, 13, 'easy')).toBe(false)
    expect(hasSeenTierStory(8, 12, 'easy')).toBe(false)
    expect(window.localStorage.getItem('git-it-tier-story:v1:7:12:easy')).toBe('seen')
  })

  it('treats blocked storage as seen so the story never reopens on every visit', () => {
    vi.spyOn(localStorage, 'getItem').mockImplementation(() => {
      throw new DOMException('Blocked', 'SecurityError')
    })

    expect(hasSeenTierStory(7, 12, 'easy')).toBe(true)
  })

  it('ignores blocked storage writes', () => {
    vi.spyOn(localStorage, 'setItem').mockImplementation(() => {
      throw new DOMException('Blocked', 'QuotaExceededError')
    })

    expect(() => markTierStorySeen(7, 12, 'easy')).not.toThrow()
  })
})
