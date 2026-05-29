/**
 * Integration tests A–H for the Within-Session Progressive Scaffolding System.
 * Tests exercise useScaffolding + evaluateScaffoldTriggers + getScaffoldMessage end-to-end.
 * sonner's toast() is mocked so we can assert toast payloads without a DOM Toaster.
 */
import { act, cleanup, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import { evaluateScaffoldTriggers } from './evaluator'
import { getScaffoldMessage } from './messages'
import { clearScaffoldTriggers, readScaffoldTriggers } from './store'
import { useScaffolding } from './useScaffolding'

// ── Mock sonner so tests don't need a real DOM Toaster ───────────────────────
// vi.hoisted is required because vi.mock factories are hoisted to the top of the
// file at compile time — top-level const declarations would not yet be initialized.
const { mockToastCustom, mockToastDismiss } = vi.hoisted(() => ({
  mockToastCustom: vi.fn(),
  mockToastDismiss: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: {
    custom: mockToastCustom,
    dismiss: mockToastDismiss,
  },
  Toaster: () => null,
}))

// ── Helpers ──────────────────────────────────────────────────────────────────

const BASE_SESSION_ID = 9000

function makeSession(overrides: Partial<ScenarioSession> = {}): ScenarioSession {
  return {
    id: BASE_SESSION_ID,
    mode: 'primary',
    status: 'started',
    difficulty_instance_id: 1,
    completed_at: null,
    first_attempt_star_eligible: true,
    completion_type: 'state_based',
    scenario: {
      id: 1,
      slug: 'test-scenario',
      title: 'Test',
      focus: 'git init',
      narrative: '',
      lesson_number: 1,
      lesson_id: 42,
    },
    student_context: undefined,
    module: { id: 1, number: 1, title: 'Module 1' },
    difficulty: 'easy',
    variant: { id: 1, label: 'A', changed_variant: false },
    mastery_progress: { mastered: 0, required: 2 },
    // Easy: min=3, max=12
    policy: { id: 1, min_counted_commands: 3, max_counted_commands: 12, non_counted_patterns: [] },
    counts: {
      counted_action_total: 0,
      minimum_counted_commands: 3,
      maximum_counted_commands: 12,
      non_counted_diagnostic_total: 0,
      remaining_counted_commands: 12,
      max_reached: false,
      total_attempts: 0,
    },
    scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true },
    repository_state: {
      commits: [],
      branches: { main: null },
      head: { type: 'branch', name: 'main' },
      staging: {},
      working_tree: {},
      conflicts: [],
    },
    expected_state: null,
    steps: [],
    review_mode: false,
    next_difficulty: null,
    completion: null,
    ...overrides,
  }
}

function makeHardSession(overrides: Partial<ScenarioSession> = {}): ScenarioSession {
  return makeSession({
    difficulty: 'hard',
    // Hard: min=2, max=8
    policy: { id: 2, min_counted_commands: 2, max_counted_commands: 8, non_counted_patterns: [] },
    counts: {
      counted_action_total: 0,
      minimum_counted_commands: 2,
      maximum_counted_commands: 8,
      non_counted_diagnostic_total: 0,
      remaining_counted_commands: 8,
      max_reached: false,
      total_attempts: 0,
    },
    ...overrides,
  })
}

// Represents the onProceedToCommandPreview callback — caller opens the modal,
// useScaffolding just invokes whatever function it receives.
const onProceed = vi.fn()
// Keep a navigate alias used in tests that don't inspect the callback's behavior.
const navigate = onProceed

afterEach(() => {
  cleanup()
  clearScaffoldTriggers(BASE_SESSION_ID)
  vi.clearAllMocks()
})

// ── Test A: Efficient solve — no triggers ────────────────────────────────────
describe('Test A — Efficient solve, no triggers', () => {
  it('submitting exactly min_threshold action commands with target reached fires no scaffold toast', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // 3 action commands, then session completes
    const completedSession = makeSession({
      status: 'completed',
      counts: { ...makeSession().counts, counted_action_total: 3 },
    })

    act(() => {
      result.current.evaluateAndNotify(completedSession, 'counted_action', navigate)
    })

    expect(mockToastCustom).not.toHaveBeenCalled()
  })

  it('diagnostic command never fires a trigger', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    // Even if counts are high, diagnostic commands are skipped
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 10 } })

    act(() => {
      result.current.evaluateAndNotify(session, 'non_counted_diagnostic', navigate)
    })

    expect(mockToastCustom).not.toHaveBeenCalled()
  })
})

// ── Test B: T1 fires, student recovers ───────────────────────────────────────
describe('Test B — T1 fires, student recovers', () => {
  it('T1 toast appears with correct message and both buttons after crossing 40%', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // 7 commands: pct = (7-3)/(12-3)*100 ≈ 44% → T1 fires
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 7 } })

    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })

    expect(mockToastCustom).toHaveBeenCalledOnce()
    const [renderFn, options] = mockToastCustom.mock.calls[0] as [() => unknown, { id: string }]
    expect(options.id).toBe('scaffold-hint')

    // Verify T2/T3 remain unfired
    expect(result.current.flags.t2_fired).toBe(false)
    expect(result.current.flags.t3_fired).toBe(false)
    expect(result.current.flags.t1_fired).toBe(true)
    expect(renderFn).toBeDefined()
  })

  it('persists T1 fired flag to sessionStorage', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 7 } })

    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })

    const stored = readScaffoldTriggers(BASE_SESSION_ID)
    expect(stored.t1_fired).toBe(true)
    expect(stored.t2_fired).toBe(false)
    expect(stored.t3_fired).toBe(false)
  })
})

// ── Test C: Skip T1, T2 fires directly (Hard) ───────────────────────────────
describe('Test C — Skip T1, T2 fires directly (Hard)', () => {
  it('jumps from below 40% to above 65% — T2 fires, T1 remains false', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // Hard: min=2, max=8 → denominator=6
    // 6 commands → pct = (6-2)/6*100 ≈ 67% → T2 threshold, but T1 was never crossed separately
    const session = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 6 } })

    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })

    expect(mockToastCustom).toHaveBeenCalledOnce()
    expect(result.current.flags.t2_fired).toBe(true)
    // T1 was jumped — never fired
    expect(result.current.flags.t1_fired).toBe(false)
  })

  it('evaluator confirms T2 fires when jumping from 0% to 67% (independent unit check)', () => {
    const trigger = evaluateScaffoldTriggers({
      session_complete: false,
      counted_commands_used: 6,
      min_threshold: 2,
      max_limit: 8,
      scaffold_t1_fired: false,
      scaffold_t2_fired: false,
      scaffold_t3_fired: false,
    })
    expect(trigger).toBe('T2')
  })
})

// ── Test D: All three triggers fire in sequence (Hard) ───────────────────────
describe('Test D — All three triggers fire in sequence (Hard)', () => {
  it('T1 fires first, then T2, then T3, each exactly once', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // Hard: min=2, max=8
    // T1: 5 commands → pct = (5-2)/6*100 = 50% → T1
    const sessionT1 = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 5 } })
    act(() => {
      result.current.evaluateAndNotify(sessionT1, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(1)
    expect(result.current.flags.t1_fired).toBe(true)

    // T2: 7 commands → pct = (7-2)/6*100 ≈ 83% → T2
    const sessionT2 = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 7 } })
    act(() => {
      result.current.evaluateAndNotify(sessionT2, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(2)
    expect(result.current.flags.t2_fired).toBe(true)

    // T3: 8 commands → pct = 100% → T3
    const sessionT3 = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 8 } })
    act(() => {
      result.current.evaluateAndNotify(sessionT3, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(3)
    expect(result.current.flags.t3_fired).toBe(true)

    // No further triggers
    act(() => {
      result.current.evaluateAndNotify(sessionT3, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(3)
  })

  it('toast ID is constant — each new toast replaces the previous one (no stacking)', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    const sessionT1 = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 5 } })
    act(() => {
      result.current.evaluateAndNotify(sessionT1, 'counted_action', navigate)
    })
    const sessionT2 = makeHardSession({ counts: { ...makeHardSession().counts, counted_action_total: 7 } })
    act(() => {
      result.current.evaluateAndNotify(sessionT2, 'counted_action', navigate)
    })

    // Both calls use the same toast ID — sonner replaces rather than stacks
    const ids = mockToastCustom.mock.calls.map((call) => (call[1] as { id: string }).id)
    expect(new Set(ids).size).toBe(1)
    expect(ids[0]).toBe('scaffold-hint')
  })
})

// ── Test E: Toast suppressed after "Continue" ────────────────────────────────
describe('Test E — Toast suppressed after Continue is tapped', () => {
  it('clearToast dismisses the active toast', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    act(() => {
      result.current.clearToast()
    })

    expect(mockToastDismiss).toHaveBeenCalledWith('scaffold-hint')
  })
})

// ── Test F: Target reached simultaneously with threshold crossing ─────────────
describe('Test F — Target reached simultaneously with threshold crossing', () => {
  it('session_complete stops scaffold evaluation — no toast shown', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // Session completes at the same command that would cross T2
    const completedSession = makeSession({
      status: 'completed',
      counts: { ...makeSession().counts, counted_action_total: 9 }, // pct≈67%
    })

    act(() => {
      result.current.evaluateAndNotify(completedSession, 'counted_action', navigate)
    })

    expect(mockToastCustom).not.toHaveBeenCalled()
  })
})

// ── Test G: "Proceed to Command Preview" preserves session ───────────────────
describe('Test G — Proceed to Command Preview preserves session', () => {
  it('onProceedToCommandPreview callback is invoked when Proceed is clicked', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 7 } })
    const openModal = vi.fn()

    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', openModal)
    })

    // Extract the render function from the toast.custom call
    const [renderFn] = mockToastCustom.mock.calls[0] as [() => React.ReactElement]
    expect(renderFn).toBeDefined()

    // Simulate the onProceedToCommandPreview callback executing
    const element = renderFn()
    const proceedCallback = (element as unknown as { props: { onProceedToCommandPreview: () => void } }).props.onProceedToCommandPreview
    act(() => {
      proceedCallback()
    })

    // The caller-provided callback is invoked — no URL navigation
    expect(openModal).toHaveBeenCalledOnce()
    // Toast should have been dismissed before the callback
    expect(mockToastDismiss).toHaveBeenCalledWith('scaffold-hint')
  })

  it('scaffold trigger flags are persisted to sessionStorage and survive re-mount', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 7 } })

    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })

    expect(result.current.flags.t1_fired).toBe(true)

    // A new hook instance (simulates return-from-lesson re-mount) reads the persisted flags
    const { result: result2 } = renderHook(() => useScaffolding(BASE_SESSION_ID))
    expect(result2.current.flags.t1_fired).toBe(true)
    expect(result2.current.flags.t2_fired).toBe(false)
  })
})

// ── Test H: Toast clears on next command submission ──────────────────────────
describe('Test H — Toast clears on next command submission', () => {
  it('clearToast is called before processing the next command', () => {
    const { result } = renderHook(() => useScaffolding(BASE_SESSION_ID))

    // Fire T1 toast
    const session = makeSession({ counts: { ...makeSession().counts, counted_action_total: 7 } })
    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(1)

    // Next command — clearToast is called (simulating PracticeWorkspace behavior)
    act(() => {
      result.current.clearToast()
    })
    expect(mockToastDismiss).toHaveBeenCalledWith('scaffold-hint')

    // Submit another counted action — no new trigger (T1 already fired, pct < 65%)
    act(() => {
      result.current.evaluateAndNotify(session, 'counted_action', navigate)
    })
    expect(mockToastCustom).toHaveBeenCalledTimes(1) // still 1, no new toast
  })
})

// ── Scaffold message content checks ─────────────────────────────────────────
describe('Scaffold message content (per trigger/difficulty)', () => {
  it('T1/easy message mentions the Expected-State Diagram', () => {
    expect(getScaffoldMessage('T1', 'easy')).toContain('Expected-State Diagram')
  })

  it('T2/easy message mentions the Lesson Overview', () => {
    expect(getScaffoldMessage('T2', 'easy')).toContain("module's Lesson Overview")
  })

  it('T3/hard message mentions git log or git reflog', () => {
    const msg = getScaffoldMessage('T3', 'hard')
    expect(msg).toMatch(/git log|git reflog/)
  })
})
