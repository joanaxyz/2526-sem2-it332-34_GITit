import type { MonsterBodyBounds } from './monsterBodyBounds'

export type MonsterAttackOptions = {
  approachPx?: number
  /** `complete` is the gameplay default: effects fire only after the attack strip. */
  resolveAt?: 'impact' | 'complete'
  /** Pass false when the director wants to fire an effect before the monster retreats. */
  recover?: boolean
}

export type NormalizedMonsterAttackOptions = {
  approachPx?: number
  resolveAt: 'impact' | 'complete'
  recover: boolean
}

export type MonsterActorHandle = {
  /** Play an authored attack and resolve at impact or after the full strip. */
  attack: (options?: number | MonsterAttackOptions) => Promise<void>
  /** Return from the post-attack position back to the duel lane. */
  recover: () => Promise<void>
  hurt: () => Promise<void>
  /** Death strip, then hold the final frame. */
  die: () => Promise<void>
  /** Park off-screen before the travel pan begins. */
  prepOffscreen: (offsetPx: number) => void
  /** Enter from offstage and stop at the requested wide-frame hold. */
  walkIn: (fromPx?: number, ms?: number, toPx?: number) => Promise<void>
  /** Ease from the wide-frame hold into the centered duel slot. */
  slideTo: (toPx: number, ms?: number) => Promise<void>
  /** Visible idle-pixel bounds, excluding transparent sheet padding. */
  bodyBounds: () => MonsterBodyBounds | null
  element: () => HTMLDivElement | null
}
