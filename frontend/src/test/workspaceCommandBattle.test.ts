import { QueryClient } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'

import type { ChallengeCommandResponse, ChallengeRun } from '@/features/challenges/types'
import { createChallengeWorkspaceCommandHandler } from '@/features/challenges/utils/challengeWorkspaceCommand'
import type { TierCommandResponse } from '@/features/story-map/components/tierWorkspaceTypes'
import { createTierWorkspaceCommandHandler } from '@/features/story-map/utils/tierWorkspaceCommand'
import { queryKeys } from '@/shared/api/queryKeys'
import { executeTerminalCommand } from '@/shared/git/simulator/engine'
import { normalizeState } from '@/shared/git/simulator/state'
import type { CommandSubmissionOutcome } from '@/shared/level-runtime/commandOutcome'

type HandlerOptions = Parameters<typeof createChallengeWorkspaceCommandHandler>[0]
  & Parameters<typeof createTierWorkspaceCommandHandler>[0]
type CommandResponse = ChallengeCommandResponse & TierCommandResponse

function setup(createHandler: typeof createChallengeWorkspaceCommandHandler | typeof createTierWorkspaceCommandHandler, command: string) {
  const queryClient = new QueryClient()
  const run = {
    id: 1,
    status: 'started',
    replay: true,
    policy: {
      scoring_policy_version: 2,
      min_counted_commands: 1,
      generous_counted_commands: 3,
      max_counted_commands: 5,
    } satisfies ChallengeRun['policy'],
    counts: { counted_action_total: 0, maximum_counted_commands: 5 },
  }
  queryClient.setQueryData(queryKeys.challengeRun(1), run)
  queryClient.setQueryData(queryKeys.adventureTierRun(1), run)
  const { execution } = executeTerminalCommand(normalizeState({}), command)
  let onSuccess!: (response: CommandResponse) => void
  let onError!: () => void
  const mutate = vi.fn((_command: string, callbacks: { onSuccess: typeof onSuccess; onError: typeof onError }) => {
    onSuccess = callbacks.onSuccess
    onError = callbacks.onError
    return execution
  })
  const battleDirector = {
    onAttackStart: vi.fn(),
    onResolve: vi.fn(),
    onError: vi.fn(),
    currentMonsters: () => [{ id: 1, species: 'bone-soldier', hp: 2, max_hp: 2, alive: true }],
  }
  const dagAnimation = {
    activity: 'idle' as const,
    animating: false,
    onCommandStart: vi.fn(),
    onCommandResolved: vi.fn(),
    onCommandError: vi.fn(),
  }
  const handler = createHandler({
    runId: 1,
    mutation: { isPending: false, mutate } as unknown as HandlerOptions['mutation'],
    battleDirector: battleDirector as unknown as HandlerOptions['battleDirector'],
    dagAnimation,
    queryClient,
    clearToast: vi.fn(),
    evaluateAndNotify: vi.fn(),
    setExitConfirmOpen: vi.fn(),
    setWorkspaceEditorPath: vi.fn(),
    queueOutcomeAnimation: vi.fn(),
    onSkillsLearned: vi.fn(),
  })
  const outcome: CommandSubmissionOutcome = {
    processed: execution.processed,
    counted: !execution.processed || !execution.diagnostic,
    solved: false,
    failed: false,
    command_family: execution.command_family ?? '',
    previous_rules_passing: 0,
    rules_passing: 0,
    rules_delta: 0,
    total_rules: 2,
    max_counted_commands: 5,
    counted_command_count: 0,
    remaining_counted_commands: 5,
  }
  return {
    handler,
    mutate,
    battleDirector,
    dagAnimation,
    succeed: (overrides: Partial<CommandSubmissionOutcome> = {}) => onSuccess({
      run,
      command_family: execution.command_family,
      command_outcome: { ...outcome, ...overrides },
      step: { command_classification: 'diagnostic' },
    } as unknown as CommandResponse),
    fail: () => onError(),
  }
}

describe.each([
  ['challenge', createChallengeWorkspaceCommandHandler],
  ['adventure', createTierWorkspaceCommandHandler],
] as const)('%s workspace command effects', (_mode, createHandler) => {
  it.each(['cd ..', 'ls', 'pwd', 'mkdir src', 'echo hello > README.md', 'gti status'])('executes %s without command effects', (command) => {
    const { handler, mutate, battleDirector, dagAnimation, succeed } = setup(createHandler, command)

    handler(command)
    // Exercise both the immediate local prediction and a different server verdict.
    succeed({ rules_passing: 1, rules_delta: 1 })

    expect(mutate).toHaveBeenCalledWith(command, expect.any(Object))
    expect(battleDirector.onAttackStart).not.toHaveBeenCalled()
    expect(battleDirector.onResolve).not.toHaveBeenCalled()
    expect(dagAnimation.onCommandStart).not.toHaveBeenCalled()
    expect(dagAnimation.onCommandResolved).not.toHaveBeenCalled()
  })

  it('does not cancel an existing attack or flash the graph when a shell submission fails', () => {
    const { handler, battleDirector, dagAnimation, fail } = setup(createHandler, 'cd ..')
    handler('cd ..')
    fail()

    expect(battleDirector.onError).not.toHaveBeenCalled()
    expect(dagAnimation.onCommandError).not.toHaveBeenCalled()
  })

  it.each(['git status', 'git init', 'git comit'])('keeps command effects for %s', (command) => {
    const { handler, battleDirector, dagAnimation, succeed } = setup(createHandler, command)
    handler(command)
    succeed()

    expect(battleDirector.onAttackStart).toHaveBeenCalledOnce()
    expect(battleDirector.onResolve).toHaveBeenCalled()
    expect(battleDirector.onResolve.mock.calls[0][0].events[0]).toMatchObject({ type: 'player_attack' })
    expect(dagAnimation.onCommandStart).toHaveBeenCalledOnce()
    expect(dagAnimation.onCommandResolved).toHaveBeenCalled()
  })
})
