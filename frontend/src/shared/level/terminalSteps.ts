import type { TerminalLine, TerminalStep } from './types'

// Sentinel result categories used only for client-side optimistic placeholders.
// Real server steps use the backend's RESULT_* values (TargetMatched, etc.).
const PENDING_RESULT = 'Pending'
const ERROR_RESULT = 'Error'

const TARGET_MATCHED_RESULT = 'TargetMatched'

// Optimistic steps get monotonically-decreasing negative ids so they never
// collide with real (positive) server ids, across attempts or features.
let ephemeralStepId = 0

export function nextEphemeralStepId() {
  ephemeralStepId -= 1
  return ephemeralStepId
}

export function isEphemeralStep(step: { id: number }) {
  return step.id < 0
}

export function stripEphemeralSteps<T extends { id: number }>(steps: T[]): T[] {
  return steps.filter((step) => !isEphemeralStep(step))
}

export function createPendingStep(command: string, id: number): TerminalStep {
  return { id, command_text: command, terminal_output: '', result_category: PENDING_RESULT }
}

export function createErrorStep(command: string, message: string, id: number): TerminalStep {
  return { id, command_text: command, terminal_output: message, result_category: ERROR_RESULT }
}

// Single source of truth for how a command step renders in the terminal, so the
// adventure and challenge terminals are visually identical. Git errors render as
// plain output (matching challenge); only the client error placeholder is amber.
export function terminalLinesFromSteps(steps: TerminalStep[]): TerminalLine[] {
  const lines: TerminalLine[] = []
  for (const step of steps) {
    lines.push({ id: `input-${step.id}`, kind: 'input', text: step.command_text })
    lines.push({
      id: `output-${step.id}`,
      kind:
        step.result_category === TARGET_MATCHED_RESULT
          ? 'success'
          : step.result_category === ERROR_RESULT
            ? 'warning'
            : 'output',
      text: step.result_category === PENDING_RESULT ? '...' : step.terminal_output,
    })
  }
  return lines
}
