import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { readPreference, usePersistentState, writePreference } from './persistentState'

const STORAGE_PREFIX = 'git-it:pref:'

afterEach(() => {
  window.localStorage.clear()
})

describe('readPreference / writePreference', () => {
  it('round-trips JSON-serialisable values under the preference namespace', () => {
    writePreference('demo', { ratio: 0.42 })

    expect(window.localStorage.getItem(`${STORAGE_PREFIX}demo`)).toBe('{"ratio":0.42}')
    expect(readPreference('demo', { ratio: 0 })).toEqual({ ratio: 0.42 })
  })

  it('returns the fallback when a key is missing', () => {
    expect(readPreference('missing', 'fallback')).toBe('fallback')
  })

  it('drops and falls back on corrupt JSON', () => {
    window.localStorage.setItem(`${STORAGE_PREFIX}broken`, '{not json')

    expect(readPreference('broken', 7)).toBe(7)
    expect(window.localStorage.getItem(`${STORAGE_PREFIX}broken`)).toBeNull()
  })
})

describe('usePersistentState', () => {
  it('hydrates from storage and persists subsequent changes', () => {
    writePreference('count', 3)

    const { result } = renderHook(() => usePersistentState('count', 0))
    expect(result.current[0]).toBe(3)

    act(() => result.current[1](5))

    expect(result.current[0]).toBe(5)
    expect(readPreference('count', 0)).toBe(5)
  })

  it('does not persist the default for untouched preferences', () => {
    renderHook(() => usePersistentState('untouched', 'default'))

    expect(window.localStorage.getItem(`${STORAGE_PREFIX}untouched`)).toBeNull()
  })

  it('runs the sanitizer over the hydrated value', () => {
    writePreference('ratio', 99)

    const clampRatio = (value: number) => Math.min(Math.max(value, 0), 1)
    const { result } = renderHook(() => usePersistentState('ratio', 0.5, clampRatio))

    expect(result.current[0]).toBe(1)
  })
})
