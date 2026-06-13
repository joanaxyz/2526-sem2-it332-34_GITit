import type { BattleBlock, BattleEvent, BattleMonster } from '@/shared/battle/types'

/**
 * Client-side fallback for surfaces whose backend `battle` block hasn't
 * shipped: synthesizes the same contract from signals the responses already
 * carry (solved flag, command classification, objective-check deltas), so the
 * stage consumes exactly one shape either way. Swapped out per-surface the
 * moment `response.battle` appears.
 */

const MOB_CYCLE = ['slime', 'skeleton', 'archer', 'swordsman', 'skeleton-archer', 'armored-orc']
const ELITE_CYCLE = ['armored-skeleton', 'knight', 'greatsword-skeleton', 'lancer']
const BOSS_CYCLE = ['werebear', 'knight-templar', 'elite-orc', 'werewolf', 'wizard', 'priest']

export type DeriveInput = {
  /** Level/target solved by this command. */
  solved: boolean
  /** Counted toward the budget (state-mutating or failed git command). */
  counted: boolean
  /** Made measurable progress (new objective checks satisfied, or solved). */
  progressed: boolean
  /** Command family for the effect registry ("commit", "merge", …). */
  skill: string
  /** Budget exhausted by this command → defeat. */
  defeated: boolean
  /** Roster before this command (the director's local copy). */
  monsters: BattleMonster[]
}

/** Command family for the effect registry: "git commit -m x" → "commit". */
export function commandSkill(command: string): string {
  const tokens = command.trim().split(/\s+/)
  if (tokens[0] !== 'git' || !tokens[1]) return 'default'
  return tokens[1].toLowerCase()
}

/** How many checklist rows are ticked (objective progress signal). */
export function countSatisfied(checks: Array<{ satisfied: boolean }> | null | undefined): number {
  return (checks ?? []).reduce((n, check) => n + (check.satisfied ? 1 : 0), 0)
}

/**
 * Deterministic adventure roster for level N of M when the server doesn't
 * provide one: early levels get 1–2 mobs, the back third adds an elite.
 */
export function clientAdventureRoster(levelIndex: number, totalLevels: number): BattleMonster[] {
  const lateGame = totalLevels > 0 && levelIndex >= Math.floor((totalLevels * 2) / 3)
  const roster: BattleMonster[] = [
    {
      id: 0,
      species: MOB_CYCLE[levelIndex % MOB_CYCLE.length],
      tier: 'mob',
      hp: 2,
      max_hp: 2,
      alive: true,
    },
  ]
  if (levelIndex % 2 === 1) {
    roster.push({
      id: 1,
      species: MOB_CYCLE[(levelIndex + 3) % MOB_CYCLE.length],
      tier: 'mob',
      hp: 2,
      max_hp: 2,
      alive: true,
    })
  }
  if (lateGame) {
    roster.push({
      id: roster.length,
      species: ELITE_CYCLE[levelIndex % ELITE_CYCLE.length],
      tier: 'elite',
      hp: 3,
      max_hp: 3,
      alive: true,
    })
  }
  return roster
}

/** Deterministic challenge boss when the server doesn't provide one. */
export function clientChallengeRoster(levelId: number, maxCounted: number): BattleMonster[] {
  const hp = Math.max(3, Math.min(8, maxCounted))
  return [
    {
      id: 0,
      species: BOSS_CYCLE[levelId % BOSS_CYCLE.length],
      tier: 'boss',
      hp,
      max_hp: hp,
      alive: true,
    },
  ]
}

export function deriveBattleEvents(input: DeriveInput): BattleBlock {
  const monsters = input.monsters.map((m) => ({ ...m }))
  const events: BattleEvent[] = []
  const alive = () => monsters.filter((m) => m.alive)

  if (input.solved) {
    // Finishing blow: everything left dies.
    for (const monster of alive()) {
      const remaining = monster.hp
      monster.hp = 0
      monster.alive = false
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: monster.id,
        damage: remaining,
        target_hp_after: 0,
      })
      events.push({ type: 'monster_death', monster: monster.id })
    }
    events.push({ type: 'encounter_cleared' })
  } else if (input.counted && input.progressed) {
    const target = alive()[0]
    if (target) {
      target.hp = Math.max(0, target.hp - 1)
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: target.id,
        damage: 1,
        target_hp_after: target.hp,
      })
      if (target.hp === 0) {
        target.alive = false
        events.push({ type: 'monster_death', monster: target.id })
      }
    }
  } else if (input.counted) {
    // Miss: a monster takes the free shot. Pure drama — the cost was the mana.
    const attacker = alive()[alive().length - 1]
    if (attacker) {
      events.push({ type: 'monster_attack', monster: attacker.id, cause: 'miss' })
    }
  }

  if (input.defeated) events.push({ type: 'player_defeat' })

  return { schema_version: 1, monsters, events }
}
