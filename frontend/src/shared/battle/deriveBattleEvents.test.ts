import { describe, expect, it } from 'vitest'

import {
  clientAdventureRoster,
  clientChallengeRoster,
  commandSkill,
  countSatisfied,
  deriveBattleEvents,
} from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster } from '@/shared/battle/types'

function mob(id: number, hp = 1, alive = true): BattleMonster {
  return { id, species: 'slime', tier: 'mob', hp, max_hp: hp, alive }
}

function input(overrides: Partial<Parameters<typeof deriveBattleEvents>[0]> = {}) {
  return {
    solved: false,
    counted: true,
    progressed: false,
    skill: 'commit',
    defeated: false,
    monsters: [mob(0)],
    ...overrides,
  }
}

describe('commandSkill', () => {
  it('extracts the git subcommand', () => {
    expect(commandSkill('git commit -m "x"')).toBe('commit')
    expect(commandSkill('  git   PUSH origin main')).toBe('push')
  })

  it('falls back to default for non-git input', () => {
    expect(commandSkill('ls -la')).toBe('default')
    expect(commandSkill('git')).toBe('default')
  })
})

describe('countSatisfied', () => {
  it('counts ticked objective rows and tolerates null', () => {
    expect(countSatisfied([{ satisfied: true }, { satisfied: false }, { satisfied: true }])).toBe(2)
    expect(countSatisfied(null)).toBe(0)
    expect(countSatisfied(undefined)).toBe(0)
  })
})

describe('deriveBattleEvents', () => {
  it('solving lands a finishing blow on every living monster', () => {
    const block = deriveBattleEvents(input({ solved: true, monsters: [mob(0, 3), mob(1, 2)] }))
    expect(block.events.map((e) => e.type)).toEqual([
      'player_attack',
      'monster_death',
      'player_attack',
      'monster_death',
      'encounter_cleared',
    ])
    expect(block.monsters.every((m) => !m.alive)).toBe(true)
  })

  it('a counted command with progress hits the front monster', () => {
    const block = deriveBattleEvents(input({ progressed: true, monsters: [mob(0, 2), mob(1, 1)] }))
    expect(block.events.map((e) => e.type)).toEqual(['player_attack'])
    expect(block.monsters[0].hp).toBe(1)
  })

  it('a counted command with no progress draws a miss from the rear monster', () => {
    const block = deriveBattleEvents(input({ progressed: false, monsters: [mob(0), mob(1)] }))
    expect(block.events).toEqual([{ type: 'monster_attack', monster: 1, cause: 'miss' }])
  })

  it('a non-counted command is a free action (no events)', () => {
    expect(deriveBattleEvents(input({ counted: false })).events).toEqual([])
  })

  it('appends a defeat event when the budget is exhausted', () => {
    const block = deriveBattleEvents(input({ progressed: false, defeated: true }))
    expect(block.events.map((e) => e.type)).toEqual(['monster_attack', 'player_defeat'])
  })

  it('does not mutate the input roster', () => {
    const monsters = [mob(0, 2)]
    deriveBattleEvents(input({ progressed: true, monsters }))
    expect(monsters[0].hp).toBe(2)
  })
})

describe('client fallback rosters', () => {
  it('builds a deterministic challenge boss with budget-bounded HP', () => {
    expect(clientChallengeRoster(0, 5)).toEqual([
      { id: 0, species: 'werebear', tier: 'boss', hp: 5, max_hp: 5, alive: true },
    ])
    // HP is clamped to [3, 8].
    expect(clientChallengeRoster(0, 1)[0].hp).toBe(3)
    expect(clientChallengeRoster(0, 99)[0].hp).toBe(8)
  })

  it('adds an elite to the back third of an adventure', () => {
    expect(clientAdventureRoster(0, 9).some((m) => m.tier === 'elite')).toBe(false)
    expect(clientAdventureRoster(8, 9).some((m) => m.tier === 'elite')).toBe(true)
  })
})
