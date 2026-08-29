import { describe, expect, it } from 'vitest'
import { evaluateScaffoldTriggers } from './evaluator'
import type { ScaffoldEvaluationInput } from './evaluator'

// min=3, max=12  ->  denominator = 9
// min=2, max=8   ->  denominator = 6
function makeState(overrides: Partial<ScaffoldEvaluationInput> = {}): ScaffoldEvaluationInput {
  return {
    session_complete: false,
    counted_commands_used: 0,
    min_threshold: 3,
    max_limit: 12,
    scaffold_t1_fired: false,
    scaffold_t2_fired: false,
    scaffold_t3_fired: false,
    ...overrides,
  }
}

describe('evaluateScaffoldTriggers', () => {
  it('returns null when session_complete is true regardless of pct', () => {
    const state = makeState({ session_complete: true, counted_commands_used: 12 })
    expect(evaluateScaffoldTriggers(state)).toBeNull()
  })

  it('returns null when below all thresholds', () => {
    // pct = (5-3)/(12-3)*100 < 22% - below 40%
    expect(evaluateScaffoldTriggers(makeState({ counted_commands_used: 5 }))).toBeNull()
  })

  it('returns T1 when pct crosses 40%', () => {
    // pct = (7-3)/9*100 < 44% - T1 threshold (40%)
    expect(evaluateScaffoldTriggers(makeState({ counted_commands_used: 7 }))).toBe('T1')
  })

  it('returns T2 when pct crosses 65%', () => {
    // pct = (9-3)/9*100 < 67% - T2 threshold (65%), T1 already fired
    const state = makeState({ counted_commands_used: 9, scaffold_t1_fired: true })
    expect(evaluateScaffoldTriggers(state)).toBe('T2')
  })

  it('returns T3 when pct crosses 85%', () => {
    // pct = (11-3)/9*100 < 89% - T3 threshold (85%), T1+T2 already fired
    const state = makeState({ counted_commands_used: 11, scaffold_t1_fired: true, scaffold_t2_fired: true })
    expect(evaluateScaffoldTriggers(state)).toBe('T3')
  })

  it('skip: 30% -> 70% jump - T2 fires, T1 remains false permanently', () => {
    // First eval at 70%: T2 fires (T3 not reached)
    const beforeFire = makeState({ counted_commands_used: 9 }) // <67%
    expect(evaluateScaffoldTriggers(beforeFire)).toBe('T2')

    // After T2 fires: future eval at same pct, T1 never fires
    const afterT2 = makeState({ counted_commands_used: 9, scaffold_t2_fired: true })
    expect(evaluateScaffoldTriggers(afterT2)).toBeNull()
    expect(afterT2.scaffold_t1_fired).toBe(false) // T1 was never marked fired
  })

  it('skip: 30% -> 92% jump - T3 fires, T1 and T2 remain false permanently', () => {
    // First eval at 92%: T3 fires
    const beforeFire = makeState({ counted_commands_used: 12 }) // 100%
    expect(evaluateScaffoldTriggers(beforeFire)).toBe('T3')

    // After T3 fires: T2 and T1 never fire in future evals
    const afterT3 = makeState({ counted_commands_used: 12, scaffold_t3_fired: true })
    expect(evaluateScaffoldTriggers(afterT3)).toBeNull()
    // T1 and T2 flags remain false - they were skipped, not fired
    expect(afterT3.scaffold_t1_fired).toBe(false)
    expect(afterT3.scaffold_t2_fired).toBe(false)
  })

  it('all three fired -> null', () => {
    const state = makeState({
      counted_commands_used: 12,
      scaffold_t1_fired: true,
      scaffold_t2_fired: true,
      scaffold_t3_fired: true,
    })
    expect(evaluateScaffoldTriggers(state)).toBeNull()
  })

  it('T1 fired, then T2 threshold crossed -> T2 fires', () => {
    const state = makeState({
      counted_commands_used: 9,
      scaffold_t1_fired: true,
    }) // <67%
    expect(evaluateScaffoldTriggers(state)).toBe('T2')
  })

  it('T1 and T2 fired, then T3 threshold crossed -> T3 fires', () => {
    const state = makeState({
      counted_commands_used: 11, // <89%
      scaffold_t1_fired: true,
      scaffold_t2_fired: true,
    })
    expect(evaluateScaffoldTriggers(state)).toBe('T3')
  })

  it('after T2 fires via skip, T1 never fires in any future eval', () => {
    // Simulate: jumped past T1 (40%), T2 fired. pct stays above 65%.
    const state = makeState({ counted_commands_used: 9, scaffold_t2_fired: true })
    // T2 already fired, T3 not reached -> result is null, not T1
    expect(evaluateScaffoldTriggers(state)).toBeNull()
  })

  it('works with min=2, max=8 (hard scenario parameters)', () => {
    // 5 commands used -> pct = (5-2)/6*100 = 50% -> below T2(65%) but above T1(40%)
    const state = makeState({ counted_commands_used: 5, min_threshold: 2, max_limit: 8 })
    expect(evaluateScaffoldTriggers(state)).toBe('T1')

    // 7 commands -> pct = (7-2)/6*100 < 83% -> above T2(65%) but below T3(85%)
    const state2 = makeState({ counted_commands_used: 7, min_threshold: 2, max_limit: 8, scaffold_t1_fired: true })
    expect(evaluateScaffoldTriggers(state2)).toBe('T2')

    // 8 commands -> pct = 100% -> T3
    const state3 = makeState({
      counted_commands_used: 8,
      min_threshold: 2,
      max_limit: 8,
      scaffold_t1_fired: true,
      scaffold_t2_fired: true,
    })
    expect(evaluateScaffoldTriggers(state3)).toBe('T3')
  })
})
