import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useNewlyEarnedChestThresholds } from './useNewlyEarnedChestThresholds'

describe('useNewlyEarnedChestThresholds', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  afterEach(() => {
    delete document.documentElement.dataset.motion
    vi.useRealTimers()
  })

  it('seeds already-earned chests silently on the first-ever visit, without celebrating them', () => {
    const { result } = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(result.current.size).toBe(0)
  })

  it('celebrates a chest that is newly earned on a later visit (e.g. after finishing a level elsewhere)', () => {
    // First visit establishes the baseline at [25].
    const { unmount } = renderHook(() => useNewlyEarnedChestThresholds(1, [25]))
    unmount()

    // A later visit (a fresh mount, as happens after returning from a level
    // run) sees 50 crossed for the first time and should celebrate it.
    const { result } = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(result.current.has(50)).toBe(true)
    expect(result.current.has(25)).toBe(false)
  })

  it('flags a chest that crosses its threshold while mounted, then clears it after the animation window', () => {
    vi.useFakeTimers()
    const { result, rerender } = renderHook(
      ({ earned }: { earned: number[] }) => useNewlyEarnedChestThresholds(1, earned),
      { initialProps: { earned: [25] } },
    )
    expect(result.current.size).toBe(0)

    rerender({ earned: [25, 50] })
    expect(result.current.has(50)).toBe(true)

    act(() => {
      vi.advanceTimersByTime(1300)
    })
    expect(result.current.has(50)).toBe(false)
  })

  it('does not re-celebrate a chest on a subsequent visit', () => {
    const { unmount } = renderHook(() => useNewlyEarnedChestThresholds(1, [25]))
    unmount()
    const first = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(first.result.current.has(50)).toBe(true)
    first.unmount()

    const second = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(second.result.current.size).toBe(0)
  })

  it('tracks chapters independently', () => {
    const chapterOne = renderHook(() => useNewlyEarnedChestThresholds(1, [25]))
    chapterOne.unmount()

    // Chapter 2 has never been seen, so its first mount seeds silently even
    // though chapter 1 already has an established baseline.
    const chapterTwo = renderHook(() => useNewlyEarnedChestThresholds(2, [25, 50]))
    expect(chapterTwo.result.current.size).toBe(0)
  })

  it('skips the animation when the app motion setting is reduced, but still records the baseline', () => {
    const { unmount } = renderHook(() => useNewlyEarnedChestThresholds(1, [25]))
    unmount()

    document.documentElement.dataset.motion = 'reduced'
    const reduced = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(reduced.result.current.size).toBe(0)
    reduced.unmount()

    // Turning motion back on afterwards must not retroactively celebrate it.
    delete document.documentElement.dataset.motion
    const after = renderHook(() => useNewlyEarnedChestThresholds(1, [25, 50]))
    expect(after.result.current.size).toBe(0)
  })
})
