import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useChallengeDagAnimation } from '@/features/challenges/hooks/useChallengeDagAnimation'
import type { CommandSubmissionOutcome } from '@/shared/level-runtime/commandOutcome'

function outcome(overrides: Partial<CommandSubmissionOutcome> = {}): CommandSubmissionOutcome {
  return {
    processed: true,
    counted: true,
    solved: false,
    failed: false,
    command_family: 'commit',
    previous_rules_passing: 0,
    rules_passing: 1,
    rules_delta: 1,
    total_rules: 3,
    max_counted_commands: 5,
    counted_command_count: 1,
    remaining_counted_commands: 4,
    ...overrides,
  }
}

afterEach(() => {
  vi.useRealTimers()
})

describe('useChallengeDagAnimation', () => {
  it('holds graph changes while processing and then shows successful progress', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useChallengeDagAnimation())

    act(() => result.current.onCommandStart())
    expect(result.current).toMatchObject({ activity: 'processing', animating: true })

    act(() => result.current.onCommandResolved(outcome()))
    expect(result.current).toMatchObject({ activity: 'updated', animating: true })

    act(() => vi.advanceTimersByTime(899))
    expect(result.current.activity).toBe('updated')

    act(() => vi.advanceTimersByTime(1))
    expect(result.current).toMatchObject({ activity: 'idle', animating: false })
  })

  it('settles rejected commands without leaving the terminal locked', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useChallengeDagAnimation())

    act(() => result.current.onCommandStart())
    act(() => result.current.onCommandResolved(outcome({ processed: false, rules_delta: 0 })))
    expect(result.current).toMatchObject({ activity: 'error', animating: true })

    act(() => vi.advanceTimersByTime(520))
    expect(result.current).toMatchObject({ activity: 'idle', animating: false })
  })
})
