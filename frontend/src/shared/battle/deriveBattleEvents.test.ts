import { describe, expect, it } from 'vitest'

import {
  clientChallengeRoster,
  commandSkill,
  countSatisfied,
  deriveBattleEventsFromCommandOutcome,
  skillForCommand,
} from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster, CommandSubmissionOutcome } from '@/shared/battle/types'

function monster(id = 0, hp = 3): BattleMonster {
  return { id, species: 'bone-soldier', hp, max_hp: hp, alive: hp > 0 }
}

function outcome(overrides: Partial<CommandSubmissionOutcome> = {}): CommandSubmissionOutcome {
  return {
    processed: true,
    counted: true,
    solved: false,
    failed: false,
    command_family: 'commit',
    previous_rules_passing: 0,
    rules_passing: 0,
    rules_delta: 0,
    total_rules: 3,
    max_counted_commands: 5,
    counted_command_count: 1,
    remaining_counted_commands: 4,
    ...overrides,
  }
}

describe('commandSkill', () => {
  it('extracts the git subcommand', () => {
    expect(commandSkill('git commit -m test')).toBe('commit')
    expect(commandSkill('notgit')).toBe('default')
  })
})

describe('skillForCommand', () => {
  it('specializes conflict checkout/diff commands', () => {
    expect(skillForCommand('git checkout --ours file.txt', 'checkout')).toBe('checkout-conflict')
    expect(skillForCommand('git diff --base file.txt', 'diff')).toBe('diff-conflict')
  })
})

describe('countSatisfied', () => {
  it('counts satisfied rows', () => {
    expect(countSatisfied([{ satisfied: true }, { satisfied: false }, { satisfied: true }])).toBe(2)
    expect(countSatisfied(null)).toBe(0)
    expect(countSatisfied(undefined)).toBe(0)
  })
})

describe('deriveBattleEventsFromCommandOutcome', () => {
  it('plays finishing blow when solved', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ solved: true, rules_passing: 3, rules_delta: 1, remaining_counted_commands: 3 }),
      skill: 'commit',
      monsters: [monster(0, 3)],
    })

    expect(block.events.map((event) => event.type)).toEqual([
      'player_attack',
      'monster_death',
      'encounter_cleared',
    ])
    expect(block.waves[0].monsters[0].alive).toBe(false)
  })

  it('plays player attack and counter on progress', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ rules_passing: 1, rules_delta: 1 }),
      skill: 'add',
      monsters: [monster(0, 3)],
    })

    expect(block.events.map((event) => event.type)).toEqual(['player_attack', 'monster_attack'])
    expect(block.waves[0].monsters[0].hp).toBe(2)
    expect(block.player_hp).toBe(4)
  })

  it('reserves the final monster HP until the stage is actually solved', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ solved: false, rules_passing: 3, rules_delta: 1 }),
      skill: 'commit',
      monsters: [monster(0, 1)],
    })

    expect(block.events.map((event) => event.type)).toEqual(['player_attack', 'monster_attack'])
    expect(block.events).not.toContainEqual({ type: 'monster_death', monster: 0 })
    expect(block.waves[0].monsters[0]).toMatchObject({ hp: 1, alive: true })
  })

  it('casts a damage-less missed attack then a miss counter on counted no-progress', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ rules_passing: 0, rules_delta: 0 }),
      skill: 'status',
      monsters: [monster(0, 3)],
    })

    expect(block.events).toMatchObject([
      { type: 'player_attack', skill: 'status', target: 0, damage: 0, target_hp_after: 3, missed: true },
      { type: 'monster_attack', cause: 'miss' },
    ])
    expect(block.waves[0].monsters[0].hp).toBe(3)
    expect(block.waves[0].monsters[0].alive).toBe(true)
  })

  it('casts free inspection commands without damage or counterattack', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ counted: false, remaining_counted_commands: 5 }),
      skill: 'status',
      monsters: [monster(0, 3)],
    })

    expect(block.events).toEqual([
      { type: 'player_attack', skill: 'status', target: 0, damage: 0, target_hp_after: 3 },
    ])
    expect(block.waves[0].monsters[0].hp).toBe(3)
    expect(block.player_hp).toBe(5)
  })

  it('appends defeat when command outcome failed', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ failed: true, remaining_counted_commands: 0 }),
      skill: 'add',
      monsters: [monster(0, 3)],
    })

    expect(block.events.at(-1)).toEqual({ type: 'player_defeat' })
    expect(block.player_hp).toBe(0)
  })
})

describe('client roster stability', () => {
  it('selects the same monster for the same seed', () => {
    const a = clientChallengeRoster(7, 5, ['bone-archer', 'bone-ghost'], {
      seed: 'story:run:7',
      storyWorldSlug: 'arcane-spire',
    })
    const b = clientChallengeRoster(7, 5, ['bone-archer', 'bone-ghost'], {
      seed: 'story:run:7',
      storyWorldSlug: 'arcane-spire',
    })
    expect(a[0].species).toBe(b[0].species)
  })

  it('keeps existing monster max hp instead of rescaling to total rules', () => {
    const block = deriveBattleEventsFromCommandOutcome({
      outcome: outcome({ total_rules: 9, rules_passing: 1, rules_delta: 1 }),
      skill: 'add',
      monsters: [monster(0, 4)],
    })

    expect(block.waves[0].monsters[0].max_hp).toBe(4)
    expect(block.waves[0].monsters[0].hp).toBe(3)
  })
})
