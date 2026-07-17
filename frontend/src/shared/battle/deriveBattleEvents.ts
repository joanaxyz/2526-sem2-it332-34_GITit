import type { BattleBlock, BattleEvent, BattleMonster, CommandSubmissionOutcome } from '@/shared/battle/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

const FALLBACK_MONSTER_POOL = Object.keys(getStoryWorld(DEFAULT_STORY_WORLD_SLUG).battle.monsters)
const MONSTER_DAMAGE = 1

export type DeriveFromCommandOutcomeInput = {
  outcome: CommandSubmissionOutcome
  /** Exact skill-sheet key for this submitted command. */
  skill: string
  /** Roster before this command (the director's local visual copy). */
  monsters: BattleMonster[]
  /** StoryWorld used for fallback monster selection. */
  storyWorldSlug?: string | null
}

type RosterOptions = {
  /** Stable key so refreshes and re-renders keep the same visual monster. */
  seed?: string | number | null
  storyWorldSlug?: string | null
  /** Initial visual HP; should match the level's rule/command budget. */
  maxHp?: number | null
}

function gitTokens(command: string): string[] {
  return command.trim().toLowerCase().split(/\s+/).filter(Boolean)
}

/** Command family for the effect registry: "git commit -m x" -> "commit". */
export function commandSkill(command: string): string {
  const tokens = gitTokens(command)
  if (tokens[0] !== 'git' || !tokens[1]) return 'default'
  return tokens[1]
}

function normalizeSkillName(skill: string | null | undefined): string | null {
  const value = skill?.trim().toLowerCase()
  if (!value) return null
  return value.startsWith('git ') ? commandSkill(value) : value
}

/** Exact skill-sheet key for a concrete command form. */
export function skillForCommand(command: string, fallbackSkill?: string | null): string {
  const tokens = gitTokens(command)
  if (tokens[0] === 'git') {
    if (tokens[1] === 'checkout' && (tokens.includes('--ours') || tokens.includes('--theirs'))) {
      return 'checkout-conflict'
    }
    if (tokens[1] === 'diff' && (tokens.includes('--ours') || tokens.includes('--theirs') || tokens.includes('--base'))) {
      return 'diff-conflict'
    }
  }
  return normalizeSkillName(fallbackSkill) ?? commandSkill(command)
}

/** How many checklist rows are ticked (objective progress signal). */
export function countSatisfied(checks: Array<{ satisfied: boolean }> | null | undefined): number {
  return (checks ?? []).reduce((n, check) => n + (check.satisfied ? 1 : 0), 0)
}

/** Deterministic adventure roster for the frontend-only visual encounter. */
export function clientAdventureRoster(
  _levelIndex: number,
  _totalLevels: number,
  speciesPool: string[] = FALLBACK_MONSTER_POOL,
  options: RosterOptions = {},
): BattleMonster[] {
  const storyWorldSlug = options.storyWorldSlug ?? DEFAULT_STORY_WORLD_SLUG
  // Rotate by the wave index so back-to-back waves never reuse the same species
  // (the base seed is wave-independent, so `+ _levelIndex` guarantees a change).
  const species = selectSpecies(
    speciesPool,
    options.seed ?? `${storyWorldSlug}:adventure:${_totalLevels}`,
    _levelIndex,
  )
  const maxHp = Math.max(1, options.maxHp ?? 2)
  return [
    {
      id: 0,
      species,
      hp: maxHp,
      max_hp: maxHp,
      alive: true,
    },
  ]
}

/** Deterministic challenge opponent for the frontend-only visual encounter. */
export function clientChallengeRoster(
  _levelId: number,
  maxCounted: number,
  speciesPool: string[] = FALLBACK_MONSTER_POOL,
  options: RosterOptions = {},
): BattleMonster[] {
  const storyWorldSlug = options.storyWorldSlug ?? DEFAULT_STORY_WORLD_SLUG
  const hp = Math.max(3, Math.min(8, options.maxHp ?? maxCounted))
  const species = selectSpecies(speciesPool, options.seed ?? `${storyWorldSlug}:challenge:${_levelId}:${maxCounted}`)
  return [
    {
      id: 0,
      species,
      hp,
      max_hp: hp,
      alive: true,
    },
  ]
}

function selectSpecies(pool: string[], seed: string | number | null | undefined, rotate = 0): string {
  const candidates = pool.length ? pool : FALLBACK_MONSTER_POOL
  const base = Math.abs(stableHash(String(seed ?? candidates.join('|'))))
  const index = (base + Math.max(0, Math.floor(rotate))) % candidates.length
  return candidates[index] ?? FALLBACK_MONSTER_POOL[0]
}

function stableHash(value: string): number {
  let hash = 2166136261
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return hash | 0
}

export function activeBattleMonsters(block: BattleBlock | null | undefined): BattleMonster[] {
  if (!block) return []
  const wave = block.waves?.[Math.max(0, block.current_wave ?? 0)]
  return wave?.monsters ?? []
}

export function deriveBattleEventsFromCommandOutcome(input: DeriveFromCommandOutcomeInput): BattleBlock {
  const outcome = input.outcome
  const baseMonsters = input.monsters.length
    ? input.monsters
    : clientChallengeRoster(0, Math.max(1, outcome.max_counted_commands || outcome.total_rules || 1), undefined, {
        storyWorldSlug: input.storyWorldSlug,
        maxHp: Math.max(1, outcome.total_rules || outcome.max_counted_commands || 1),
        seed: `${input.storyWorldSlug ?? DEFAULT_STORY_WORLD_SLUG}:fallback:${outcome.command_family}:${outcome.max_counted_commands}`,
      })
  const monsterMaxHp = Math.max(1, baseMonsters[0]?.max_hp || outcome.total_rules || 1)
  const rulesPassing = Math.max(0, Math.min(monsterMaxHp, outcome.rules_passing || 0))
  const monsters = baseMonsters.map((m, index) => {
    if (index !== 0) return { ...m }
    // Rule progress can reach its visual cap before the objective's full success
    // contract does (for example, a final history/ordering check). Reserve the
    // last HP for the actual solved outcome so the monster cannot die while the
    // stage is still incomplete.
    const hp = Math.max(1, monsterMaxHp - rulesPassing)
    return { ...m, hp, max_hp: monsterMaxHp, alive: true }
  })
  const events: BattleEvent[] = []
  const alive = () => monsters.filter((m) => m.alive)
  const playerMaxHp = outcome.max_counted_commands
  const playerHp = outcome.remaining_counted_commands

  function monsterCounter(progressed: boolean) {
    // Only a living monster strikes back. The final HP is reserved until the
    // objective is solved, so an incomplete stage always retains its opponent.
    const attacker = alive()[0]
    if (!attacker) return
    events.push({
      type: 'monster_attack',
      monster: attacker.id,
      cause: progressed ? 'counter' : 'miss',
      skill: monsterSkill(attacker),
      damage: MONSTER_DAMAGE,
      player_hp_after: playerHp,
    })
  }

  if (outcome.solved) {
    // A solved objective clears the encounter: every still-living monster dies.
    for (const monster of monsters.filter((m) => m.alive)) {
      const damage = Math.max(1, monster.hp)
      monster.hp = 0
      monster.alive = false
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: monster.id,
        damage,
        target_hp_after: 0,
      })
      events.push({ type: 'monster_death', monster: monster.id })
    }
    events.push({ type: 'encounter_cleared' })
  } else if (outcome.counted && outcome.rules_delta > 0) {
    const target = monsters[0]
    if (target) {
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: target.id,
        damage: Math.max(1, outcome.rules_delta),
        target_hp_after: target.hp,
      })
    }
    monsterCounter(true)
  } else if (outcome.counted) {
    // No progress: the spell still casts and impacts the target for 0 damage,
    // the companion miss release replaces attack-end, and the monster counters.
    const target = alive()[0]
    if (target) {
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: target.id,
        damage: 0,
        target_hp_after: target.hp,
        missed: true,
      })
    }
    monsterCounter(false)
  } else {
    // Diagnostics are free inspections, but they should still feel responsive:
    // cast the command's spell without changing HP or inviting a counterattack.
    const target = alive()[0]
    if (target) {
      events.push({
        type: 'player_attack',
        skill: input.skill,
        target: target.id,
        damage: 0,
        target_hp_after: target.hp,
      })
    }
  }

  if (outcome.failed && !events.some((event) => event.type === 'player_defeat')) {
    events.push({ type: 'player_defeat' })
  }

  return {
    schema_version: 3,
    waves: [{ monsters }],
    current_wave: 0,
    events,
    player_hp: playerHp,
    player_max_hp: playerMaxHp,
  }
}

function monsterSkill(monster: BattleMonster): string {
  const species = monster.species
  if (species.includes('archer')) return 'arrow'
  if (species.includes('ghost')) return 'claw'
  if (species.includes('necromancer') || species.includes('lich')) return 'spell'
  return 'strike'
}
