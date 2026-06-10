import { describe, expect, it } from 'vitest'

import {
  createErrorStep,
  createPendingStep,
  isEphemeralStep,
  nextEphemeralStepId,
  stripEphemeralSteps,
  terminalLinesFromSteps,
} from '@/shared/practice/terminalSteps'
import type { TerminalStep } from '@/shared/practice/types'

describe('terminalLinesFromSteps', () => {
  it('renders each step as an input line followed by an output line', () => {
    const steps: TerminalStep[] = [
      { id: 1, command_text: 'git status', terminal_output: 'clean', result_category: 'TargetNotYetMatched' },
    ]
    expect(terminalLinesFromSteps(steps)).toEqual([
      { id: 'input-1', kind: 'input', text: 'git status' },
      { id: 'output-1', kind: 'output', text: 'clean' },
    ])
  })

  it('colors a matched target as success', () => {
    const lines = terminalLinesFromSteps([
      { id: 2, command_text: 'git commit', terminal_output: 'done', result_category: 'TargetMatched' },
    ])
    expect(lines[1]).toMatchObject({ kind: 'success', text: 'done' })
  })

  it('renders a pending placeholder as a dim ellipsis', () => {
    const lines = terminalLinesFromSteps([createPendingStep('git init', -1)])
    expect(lines[0]).toMatchObject({ kind: 'input', text: 'git init' })
    expect(lines[1]).toMatchObject({ kind: 'output', text: '...' })
  })

  it('colors a client error placeholder as a warning', () => {
    const lines = terminalLinesFromSteps([createErrorStep('boom', 'Command failed.', -2)])
    expect(lines[1]).toMatchObject({ kind: 'warning', text: 'Command failed.' })
  })

  it('renders git errors as plain output, matching the challenge terminal', () => {
    const lines = terminalLinesFromSteps([
      { id: 3, command_text: 'git frob', terminal_output: 'unknown command', result_category: 'Unprocessable' },
    ])
    expect(lines[1]).toMatchObject({ kind: 'output', text: 'unknown command' })
  })
})

describe('ephemeral step helpers', () => {
  it('issues strictly decreasing negative ids flagged as ephemeral', () => {
    const a = nextEphemeralStepId()
    const b = nextEphemeralStepId()
    expect(b).toBeLessThan(a)
    expect(isEphemeralStep({ id: a })).toBe(true)
    expect(isEphemeralStep({ id: 7 })).toBe(false)
  })

  it('strips only the negative-id placeholders', () => {
    const steps: TerminalStep[] = [
      { id: 1, command_text: 'a', terminal_output: '', result_category: 'TargetNotYetMatched' },
      { id: -1, command_text: 'b', terminal_output: '', result_category: 'Pending' },
    ]
    expect(stripEphemeralSteps(steps).map((step) => step.id)).toEqual([1])
  })
})
