import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  applyPreferences,
  defaultPreferences,
  persistPreferences,
  readStoredPreferences,
} from '@/shared/preferences/preferences'

describe('player preferences', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.removeAttribute('data-motion')
  })

  it('persists and restores valid preferences', () => {
    persistPreferences({ motion_mode: 'reduced' })

    expect(readStoredPreferences()).toEqual({ motion_mode: 'reduced' })
  })

  it('falls back safely when stored values are invalid', () => {
    window.localStorage.setItem('git-it-preferences', JSON.stringify({ motion_mode: 'fast' }))

    expect(readStoredPreferences()).toEqual(defaultPreferences)
  })

  it('resolves system preferences onto the document root', () => {
    const matchMedia = vi.fn((query: string) => ({
      matches: query.includes('color-scheme'),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
    Object.defineProperty(window, 'matchMedia', { configurable: true, value: matchMedia })

    applyPreferences(defaultPreferences)

    expect(document.documentElement.dataset.motion).toBe('full')
  })
})
