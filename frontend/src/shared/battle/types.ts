/**
 * Battle contract shared by adventures and challenges.
 *
 * Backend command submission returns neutral command_outcome data. Runtime HP,
 * monster HP, and animation events are frontend visual state derived from that
 * outcome; the backend no longer persists or returns battle_state.
 */

export type BattleMonster = {
  /** Stable within the encounter; event `monster`/`target` fields point here. */
  id: number
  /** Catalog monster id (a.k.a. `species`). The selected StoryWorld supplies its skin. */
  species: string
  tier: 'mob' | 'elite' | 'boss'
  hp: number
  max_hp: number
  alive: boolean
  /** Optional per-entry display scale override. */
  scale?: number
}

/** Why a monster struck Blue this turn. `timeout` is reserved for a future turn timer. */
export type MonsterAttackCause = 'counter' | 'miss' | 'timeout'

export type BattleEvent =
  | {
      type: 'player_attack'
      /** Command family, e.g. "commit" - keys the effect registry. */
      skill: string
      target: number
      damage: number
      target_hp_after: number
      /**
       * The command counted but made no progress: the spell still casts and
       * impacts, but deals no damage and the miss sheet plays after the impact.
       */
      missed?: boolean
    }
  | {
      type: 'monster_attack'
      monster: number
      cause: MonsterAttackCause
      /** Monster ability ("arrow", "spell", "cleave", ...). */
      skill?: string
      damage: number
      player_hp_after: number
    }
  | { type: 'monster_death'; monster: number }
  | { type: 'wave_cleared'; wave: number; next_wave: number }
  | { type: 'encounter_cleared' }
  | { type: 'player_defeat' }

export type BattleWave = {
  monsters: BattleMonster[]
}

export type BattleBlock = {
  schema_version: number
  waves: BattleWave[]
  current_wave: number
  events: BattleEvent[]
  /** Blue's frontend-derived HP. Null on replay/free-play payloads, so the bar hides. */
  player_hp?: number | null
  player_max_hp?: number | null
}

export type CommandSubmissionOutcome = {
  processed: boolean
  counted: boolean
  solved: boolean
  failed: boolean
  command_family: string
  previous_rules_passing: number
  rules_passing: number
  rules_delta: number
  total_rules: number
  max_counted_commands: number
  counted_command_count: number
  remaining_counted_commands: number
}

/** Normalized (0..1) rectangle for the authored land the fighters stand on. */
export type StageLanding = { x: number; y: number; width: number; height: number }

/**
 * Authored battle-stage backdrop for a content definition. The backdrop always
 * pans with the battle camera (the asset itself knows whether it's a still image
 * or a spritesheet). Null/absent -> the seeded global hall backdrop. `landing`
 * is the optional platform the fighters stand on, authored in the level editor.
 */
export type BattleStage = {
  /** Optional chapter/content parallax slug. The active frontend theme resolves it to an asset. */
  parallax?: { slug: string } | null
  landing: StageLanding | null
}
