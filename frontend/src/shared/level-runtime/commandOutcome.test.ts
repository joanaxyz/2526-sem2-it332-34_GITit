import { describe, expect, it } from 'vitest'

import { confirmsPrediction, predictLocalOutcome, type CommandSubmissionOutcome } from '@/shared/level-runtime/commandOutcome'
import type { CommandExecutionPayload } from '@/shared/level/types'

function execution(overrides: Partial<CommandExecutionPayload> = {}): CommandExecutionPayload {
  return {
    processed: true,
    diagnostic: false,
    next_state: {} as CommandExecutionPayload['next_state'],
    output: '',
    normalized_command: 'git status',
    exit_code: 0,
    stdout: '',
    stderr: '',
    command_family: 'status',
    diagnostic_metadata: [],
    ...overrides,
  } as CommandExecutionPayload
}

function serverOutcome(overrides: Partial<CommandSubmissionOutcome> = {}): CommandSubmissionOutcome {
  return {
    processed: true,
    counted: false,
    solved: false,
    failed: false,
    command_family: 'status',
    previous_rules_passing: 1,
    rules_passing: 1,
    rules_delta: 0,
    total_rules: 3,
    max_counted_commands: 5,
    counted_command_count: 2,
    remaining_counted_commands: 3,
    ...overrides,
  }
}

describe('predictLocalOutcome', () => {
  it('leaves repository changes to the server', () => {
    expect(predictLocalOutcome(execution({ command_family: 'commit' }), { counted: 2, max: 5 })).toBeNull()
  })

  it('treats a read-only look as a free turn', () => {
    expect(predictLocalOutcome(execution({ diagnostic: true }), { counted: 2, max: 5 })).toMatchObject({
      processed: true,
      counted: false,
      solved: false,
      failed: false,
      counted_command_count: 2,
      remaining_counted_commands: 3,
    })
  })

  it('spends one counted command on input the engine cannot run', () => {
    expect(
      predictLocalOutcome(execution({ processed: false, command_family: '' }), { counted: 2, max: 5 }),
    ).toMatchObject({ processed: false, counted: true, failed: false, remaining_counted_commands: 2 })
  })

  it('ends the run when a miss spends the last counted command', () => {
    expect(
      predictLocalOutcome(execution({ processed: false }), { counted: 4, max: 5 }),
    ).toMatchObject({ counted: true, failed: true, remaining_counted_commands: 0 })
  })
})

describe('confirmsPrediction', () => {
  const predicted = predictLocalOutcome(execution({ diagnostic: true }), { counted: 2, max: 5 })!

  it('accepts the server playing out the same turn', () => {
    expect(confirmsPrediction(predicted, serverOutcome())).toBe(true)
  })

  it('replays when the server saw progress or a solve', () => {
    expect(confirmsPrediction(predicted, serverOutcome({ rules_passing: 2, rules_delta: 1 }))).toBe(false)
    expect(confirmsPrediction(predicted, serverOutcome({ solved: true }))).toBe(false)
  })
})

it('counts unsuccessful inspections only under the current policy', () => {
  const failed = execution({ diagnostic: true, exit_code: 128 })
  expect(predictLocalOutcome(failed, { counted: 2, max: 3, scoringPolicyVersion: 2 }))
    .toMatchObject({ counted: true, failed: true, counted_command_count: 3 })
  expect(predictLocalOutcome(failed, { counted: 2, max: 3, scoringPolicyVersion: 1 }))
    .toMatchObject({ counted: false, failed: false, counted_command_count: 2 })
})
it('does not predict a counted mistake for empty input', () => {
  expect(predictLocalOutcome(execution({ processed: false, normalized_command: '' }), { counted: 2, max: 3 })).toBeNull()
})
