import { describe, expect, it } from 'vitest'

import { battleEventsForSubmittedCommand } from '@/shared/level-runtime/commandBattle'
import type { BattleMonster, CommandSubmissionOutcome } from '@/shared/battle/types'

function mob(id = 1, hp = 2): BattleMonster {
  return { id, species: 'bone-soldier', tier: 'mob', hp, max_hp: hp, alive: hp > 0 }
}

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

describe('battleEventsForSubmittedCommand', () => {
  it('derives the same battle event contract for shared challenge/adventure command submissions', () => {
    const block = battleEventsForSubmittedCommand({
      command: 'git add README.md',
      outcome: outcome({ command_family: 'add' }),
      monsters: [mob()],
    })

    expect(block.events[0]).toMatchObject({ type: 'player_attack', skill: 'add', damage: 1 })
    expect(block.waves[0].monsters[0].hp).toBe(1)
  })

  it('falls back to the response command family when slim payloads omit one in the outcome', () => {
    const block = battleEventsForSubmittedCommand({
      command: 'git checkout --ours app.py',
      outcome: outcome({ command_family: null as unknown as string }),
      fallbackCommandFamily: 'checkout',
      monsters: [mob()],
    })

    expect(block.events[0]).toMatchObject({ type: 'player_attack', skill: 'checkout-conflict' })
  })
})
