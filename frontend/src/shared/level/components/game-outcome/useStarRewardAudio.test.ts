import { act, cleanup, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { playStarRewardSound, preloadStarRewardSounds } from '@/shared/audio/battleAudio'

import { useStarRewardAudio } from './useStarRewardAudio'

vi.mock('@/shared/audio/battleAudio', () => ({
  playStarRewardSound: vi.fn(() => vi.fn()),
  preloadStarRewardSounds: vi.fn(),
}))

const originalHidden = Object.getOwnPropertyDescriptor(document, 'hidden')

beforeEach(() => {
  vi.useFakeTimers()
  vi.clearAllMocks()
  vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: false })))
  Object.defineProperty(document, 'hidden', { configurable: true, value: false })
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
  if (originalHidden) Object.defineProperty(document, 'hidden', originalHidden)
  else Reflect.deleteProperty(document, 'hidden')
})

describe('star reward audio', () => {
  it.each([0, 1, 2, 3])('warms a %s-star result and waits for its actual reveal events', (stars) => {
    const { result, rerender } = renderHook(({ ready }) => useStarRewardAudio(stars, ready), {
      initialProps: { ready: false },
    })
    expect(preloadStarRewardSounds).toHaveBeenCalledWith(stars)
    act(() => { result.current(stars); vi.advanceTimersByTime(2000) })
    expect(playStarRewardSound).not.toHaveBeenCalled()

    rerender({ ready: true })
    // Rendering can be delayed: elapsed time alone must not fire a cue.
    act(() => vi.advanceTimersByTime(2000))
    expect(playStarRewardSound).not.toHaveBeenCalled()
    const grades = stars === 0 ? [0] : [1, 2, 3].slice(0, stars)
    for (const grade of grades) act(() => result.current(grade))
    expect(vi.mocked(playStarRewardSound).mock.calls.map(([grade]) => grade)).toEqual(grades)
  })

  it('plays each reveal only once even if its animation restarts', () => {
    const { result } = renderHook(() => useStarRewardAudio(3, true))
    act(() => { result.current(1); result.current(1); result.current(2) })
    expect(vi.mocked(playStarRewardSound).mock.calls.map(([grade]) => grade)).toEqual([1, 2])
  })

  it('plays one final-grade cue when reduced motion shows the completed artwork immediately', () => {
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true })))
    renderHook(() => useStarRewardAudio(3, true))
    act(() => vi.advanceTimersByTime(0))
    expect(playStarRewardSound).toHaveBeenCalledExactlyOnceWith(3)
    act(() => vi.advanceTimersByTime(2000))
    expect(playStarRewardSound).toHaveBeenCalledTimes(1)
  })

  it('stops the playing cue and ignores stale events after dismissal', () => {
    const { result, unmount } = renderHook(() => useStarRewardAudio(3, true))
    const playCue = result.current
    act(() => playCue(1))
    const stop = vi.mocked(playStarRewardSound).mock.results[0].value
    unmount()
    expect(stop).toHaveBeenCalledOnce()
    act(() => playCue(2))
    expect(playStarRewardSound).toHaveBeenCalledTimes(1)
  })

  it('stops the sequence when its tab is hidden and ignores deferred reveal events', () => {
    const { result } = renderHook(() => useStarRewardAudio(3, true))
    act(() => result.current(1))
    const stop = vi.mocked(playStarRewardSound).mock.results[0].value
    Object.defineProperty(document, 'hidden', { configurable: true, value: true })
    act(() => document.dispatchEvent(new Event('visibilitychange')))
    expect(stop).toHaveBeenCalledOnce()
    Object.defineProperty(document, 'hidden', { configurable: true, value: false })
    act(() => result.current(2))
    expect(playStarRewardSound).toHaveBeenCalledTimes(1)
  })
})
