// Mirrors backend/assets/sprite_actions.py. Named sprite slots the monster
// upload form exposes; frames are counted server-side from each sheet.
export const MONSTER_ACTIONS = [
  'idle',
  'walk',
  'attack',
  'hurt',
  'death',
  'portrait',
  'projectile',
] as const

export type MonsterAction = (typeof MONSTER_ACTIONS)[number]

/** Minimum sprites a monster needs to stand and land a hit in battle. */
export const REQUIRED_MONSTER_ACTIONS: MonsterAction[] = ['idle', 'attack']

/** Actions that loop while displayed; the rest play once. */
export const LOOPING_ACTIONS: MonsterAction[] = ['idle', 'walk', 'projectile']

/** Suggested default fps per action, used to prefill the upload form. */
export const DEFAULT_ACTION_FPS: Record<MonsterAction, number> = {
  idle: 8,
  walk: 10,
  attack: 11,
  hurt: 10,
  death: 8,
  portrait: 1,
  projectile: 14,
}
