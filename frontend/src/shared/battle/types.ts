/**
 * Battle contract shared by adventures and challenges.
 *
 * The backend attaches a `battle` block to every submit response: authoritative
 * HP snapshots plus an ordered `events` list the stage choreographs. Until a
 * surface's backend block ships, deriveBattleEvents.ts synthesizes the same
 * shape client-side, so the stage consumes exactly one contract.
 */

export type BattleSpriteDescriptor = {
  url: string
  frame_count: number
  columns: number
  rows: number
  frame_width: number
  frame_height: number
  fps: number
  loops?: boolean
}

export type BattleMonsterDescriptor = {
  slug: string
  label: string
  kind: string
  scale?: number
  tier?: 'mob' | 'elite' | 'boss' | (string & {})
  attack?: {
    kind?: 'melee' | 'projectile' | (string & {})
    hit_frame?: number
    lunge_px?: number
    projectile?: string
  }
  metrics?: {
    foot_offset?: number
    hp_bar_fraction?: number
  }
  sprites: Record<string, BattleSpriteDescriptor>
}

export type BattleMonster = {
  /** Stable within the encounter; event `monster`/`target` fields point here. */
  id: number
  /** Monster Asset.slug. Kept as `species` for the persisted battle schema. */
  species: string
  tier: 'mob' | 'elite' | 'boss'
  hp: number
  max_hp: number
  alive: boolean
  /** Optional per-entry display scale override. */
  scale?: number
  /** Server-supplied visual and attack data for this monster asset. */
  descriptor?: BattleMonsterDescriptor
}

/** Why a monster got a free hit. `timeout` is reserved for a future turn timer. */
export type MonsterAttackCause = 'miss' | 'timeout'

export type BattleEvent =
  | {
      type: 'player_attack'
      /** Command family, e.g. "commit" — keys the effect registry. */
      skill: string
      target: number
      damage: number
      target_hp_after: number
    }
  | {
      type: 'monster_attack'
      monster: number
      cause: MonsterAttackCause
    }
  | { type: 'monster_death'; monster: number }
  | { type: 'encounter_cleared' }
  | { type: 'player_defeat' }

/**
 * The player has no separate HP: the command budget IS Blue's mana bar
 * (rendered from the run's existing counts). A `monster_attack` is the
 * dramatic cost of a miss; running out of mana is the existing budget
 * failure, surfaced here as `player_defeat`.
 */
export type BattleBlock = {
  schema_version: number
  monsters: BattleMonster[]
  events: BattleEvent[]
}
