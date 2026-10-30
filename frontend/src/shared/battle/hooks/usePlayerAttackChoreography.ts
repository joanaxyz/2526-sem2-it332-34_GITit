import { useCallback } from 'react'
import type { MutableRefObject } from 'react'

import {
  effectForSkill,
  effectPlacementForSkill,
  warmEffectForSkill,
} from '@/shared/battle/effects/effectRegistry'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { BattleEvent, BattleMonster } from '@/shared/battle/types'

import { boundedAnimation, wait } from './battleMotion'

type Point = { x: number; y: number }
type PlayerAttackEvent = Extract<BattleEvent, { type: 'player_attack' }>

type PlayerAttackChoreographyDeps = {
  playerRef: MutableRefObject<PlayerActorHandle | null>
  effectLayerRef: MutableRefObject<HTMLDivElement | null>
  effectBackLayerRef: MutableRefObject<HTMLDivElement | null>
  monsterHandles: MutableRefObject<Map<number, MonsterActorHandle>>
  companionSlugRef: MutableRefObject<string>
  anchor: (el: Element | null, dx?: number, dy?: number, xFrac?: number, yFrac?: number) => Point
  monsterImpactAnchor: (monsterId: number, side?: 'left' | 'right') => Point
  monsterFeetAnchor: (monsterId: number) => Point
  monsterSizeScale: (monsterId: number) => number
  setMonster: (id: number, patch: Partial<BattleMonster>) => void
}

/** Plays Blue's attack animation, launches the skill effect, then snaps the target HP. */
export function usePlayerAttackChoreography({
  playerRef,
  effectLayerRef,
  effectBackLayerRef,
  monsterHandles,
  companionSlugRef,
  anchor,
  monsterImpactAnchor,
  monsterFeetAnchor,
  monsterSizeScale,
  setMonster,
}: PlayerAttackChoreographyDeps) {
  return useCallback(
    async (event: PlayerAttackEvent, animate: boolean) => {
      const player = playerRef.current
      if (animate) {
        // Usually a no-op because the entry gate already decoded this family.
        // It also covers diagnostic or newly introduced commands that were not
        // knowable when the run first opened.
        await warmEffectForSkill(event.skill, companionSlugRef.current)
        // The companion attack sheet must finish its full windup before the skill
        // leaves Blue's hands. The cast-end sheet then plays alongside the effect
        // instead of freezing the windup's final frame.
        if (player) await player.attack()
        const layer = effectLayerRef.current
        const backLayer = effectBackLayerRef.current
        const targetHandle = monsterHandles.current.get(event.target)
        const targetEl = targetHandle?.element()
        let release: Promise<void> | null = null
        const playCastEnd = () => {
          release ??= player?.endAttack(Boolean(event.missed)) ?? Promise.resolve()
          return release
        }
        if (layer && targetEl) {
          const { playback, anchor: groundAnchor } = effectPlacementForSkill(event.skill, companionSlugRef.current)
          const feetPlanted = playback === 'ground' || groundAnchor === 'feet'
          // Launch points are fractions of Blue's live-measured rendered box,
          // never fixed pixels, so the origin stories his hand/feet responsively.
          const from =
            playback === 'ground'
              ? anchor(player?.element() ?? null, 0, 0, 0.82, 0.99)
              : anchor(player?.element() ?? null, 0, 0, 0.98, 0.42)
          const bodyImpact = monsterImpactAnchor(event.target)
          const groundImpact = monsterFeetAnchor(event.target)
          const to = playback === 'projectile' ? bodyImpact : feetPlanted ? groundImpact : anchor(targetEl)
          const impactTo = playback === 'projectile' && groundAnchor === 'feet' ? groundImpact : undefined
          let markImpact = () => {}
          const impact = new Promise<void>((resolve) => {
            markImpact = resolve
          })
          const effect = effectForSkill(event.skill, companionSlugRef.current)({
            layer,
            backLayer,
            from,
            to,
            impactTo,
            sizeScale: monsterSizeScale(event.target),
            onImpact: () => markImpact(),
          })
          void playCastEnd()
          // The target reacts on contact, never after the spell has faded: a bolt
          // when it lands, a ground run when it arrives, a burst when it blooms.
          // A missed attack still casts and impacts, but the target took no
          // damage, so it never flinches. A finishing blow skips the hurt flinch
          // entirely: the death strip starts at impact (the monster_death beat
          // that follows sees the corpse and holds it).
          const lethal = !event.missed && event.target_hp_after <= 0
          if (targetHandle && !event.missed) {
            await Promise.race([impact, effect])
            if (lethal) {
              await Promise.all([effect, targetHandle.die()])
            } else if (playback === 'projectile') {
              await Promise.all([effect, boundedAnimation(targetHandle.hurt(), 420)])
            } else {
              // Target and ground effects keep washing over the body, so the
              // flinch repeats until they fade.
              let effectDone = false
              const hurtLoop = (async () => {
                while (!effectDone) {
                  await boundedAnimation(targetHandle.hurt(), 360)
                  if (!effectDone) await wait(24)
                }
              })()
              await effect.finally(() => {
                effectDone = true
              })
              await Promise.race([hurtLoop, wait(90)])
            }
          } else {
            await effect
          }
        } else {
          void playCastEnd()
        }
        await release
      } else {
        player?.cancelAttack()
      }
      setMonster(event.target, { hp: event.target_hp_after })
    },
    [
      anchor,
      companionSlugRef,
      effectBackLayerRef,
      effectLayerRef,
      monsterFeetAnchor,
      monsterHandles,
      monsterImpactAnchor,
      monsterSizeScale,
      playerRef,
      setMonster,
    ],
  )
}
