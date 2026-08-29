import { activeBattleMonsters } from '@/shared/battle/deriveBattleEvents'
import type { BattleBlock, BattleMonster } from '@/shared/battle/types'

export type BattleResolveFlags = {
  hasPlayerAttack: boolean
  hasMissAttack: boolean
  hasMonsterAttack: boolean
  hasPlayerDefeat: boolean
}

type MonsterPresentationPlan = {
  dyingMonsterIds: ReadonlySet<number>
  animatedMonsterIds: ReadonlySet<number>
}

export function battleResolveFlags(block: BattleBlock): BattleResolveFlags {
  const events = block.events
  return {
    hasPlayerAttack: events.some((event) => event.type === 'player_attack'),
    hasMissAttack: events.some((event) => event.type === 'monster_attack' && event.cause === 'miss'),
    hasMonsterAttack: events.some((event) => event.type === 'monster_attack'),
    hasPlayerDefeat: events.some((event) => event.type === 'player_defeat'),
  }
}

function monsterPresentationPlan(block: BattleBlock): MonsterPresentationPlan {
  const dyingMonsterIds = new Set(block.events.filter((event) => event.type === 'monster_death').map((event) => event.monster))
  const animatedMonsterIds = new Set(
    block.events.flatMap((event) => {
      if (event.type === 'player_attack') return [event.target]
      if (event.type === 'monster_death') return [event.monster]
      return []
    }),
  )
  return { dyingMonsterIds, animatedMonsterIds }
}

function presentMonster(
  monster: BattleMonster,
  previous: BattleMonster | undefined,
  { dyingMonsterIds, animatedMonsterIds }: MonsterPresentationPlan,
): BattleMonster {
  const dying = dyingMonsterIds.has(monster.id)
  const deferAnimatedState = Boolean(previous && animatedMonsterIds.has(monster.id))
  return {
    ...previous,
    ...monster,
    hp: deferAnimatedState ? previous!.hp : dying && !previous ? Math.max(monster.hp, monster.max_hp) : monster.hp,
    alive: deferAnimatedState ? previous!.alive : dying && previous?.alive !== false ? true : monster.alive,
  }
}

export function visibleRosterForResolve(block: BattleBlock, previousRoster: BattleMonster[]): BattleMonster[] {
  const plan = monsterPresentationPlan(block)
  const nextRoster = activeBattleMonsters(block)
  if (previousRoster.length === 0) return nextRoster.map((monster) => presentMonster(monster, undefined, plan))

  if (block.events.some((event) => event.type === 'wave_cleared')) {
    const allMonstersById = new Map(block.waves.flatMap((wave) => wave.monsters).map((monster) => [monster.id, monster]))
    return previousRoster.map((monster) => presentMonster(allMonstersById.get(monster.id) ?? monster, monster, plan))
  }

  const previousById = new Map(previousRoster.map((monster) => [monster.id, monster]))
  return nextRoster.map((monster) => presentMonster(monster, previousById.get(monster.id), plan))
}

export function visibleWaveRoster(block: BattleBlock, waveIndex: number): BattleMonster[] {
  const plan = monsterPresentationPlan(block)
  return (block.waves[waveIndex]?.monsters ?? []).map((monster) => presentMonster(monster, undefined, plan))
}
