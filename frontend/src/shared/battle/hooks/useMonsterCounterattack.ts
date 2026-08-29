import { useCallback } from 'react'
import type { MutableRefObject } from 'react'

import {
  monsterAttackEffect,
  spriteProjectile,
} from '@/shared/battle/effects/effectRegistry'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { BattleMonster } from '@/shared/battle/types'
import { monsterSkin } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

import { boundedAnimation } from './battleMotion'

type Point = { x: number; y: number }

type MonsterCounterattackDeps = {
  rosterRef: MutableRefObject<BattleMonster[]>
  playerRef: MutableRefObject<PlayerActorHandle | null>
  effectLayerRef: MutableRefObject<HTMLDivElement | null>
  effectBackLayerRef: MutableRefObject<HTMLDivElement | null>
  monsterHandles: MutableRefObject<Map<number, MonsterActorHandle>>
  storyWorldRef: MutableRefObject<StoryWorldDef>
  anchor: (el: Element | null, dx?: number, dy?: number, xFrac?: number, yFrac?: number) => Point
  setActiveMonsterId: (next: number | null) => void
  setPlayerHp: (next: number | null) => void
}

/**
 * Plays the monster's counterattack and applies Blue's HP exactly once.
 * A `lethal` strike drops Blue at impact: the death sheet plays here instead of
 * a hurt flinch, and the player_defeat beat that follows just holds the corpse.
 */
export function useMonsterCounterattack({
  rosterRef,
  playerRef,
  effectLayerRef,
  effectBackLayerRef,
  monsterHandles,
  storyWorldRef,
  anchor,
  setActiveMonsterId,
  setPlayerHp,
}: MonsterCounterattackDeps) {
  return useCallback(
    async (monsterId: number, hpAfter: number, animate: boolean, lethal = false) => {
      setActiveMonsterId(monsterId)
      let appliedDamage = false
      let recovered = false
      const applyDamage = () => {
        if (appliedDamage) return
        appliedDamage = true
        setPlayerHp(hpAfter)
      }
      const recoverMonster = async () => {
        if (recovered) return
        recovered = true
        const current = monsterHandles.current.get(monsterId)
        if (current) await boundedAnimation(current.recover(), 620)
      }

      try {
        const handle = monsterHandles.current.get(monsterId)
        const player = playerRef.current
        if (!handle || !player || !animate) {
          applyDamage()
          return
        }

        const attacker = rosterRef.current.find((monster) => monster.id === monsterId)
        const def = attacker
          ? definitionForMonster(attacker, monsterSkin(storyWorldRef.current, attacker.species))
          : null
        const layer = effectLayerRef.current
        const backLayer = effectBackLayerRef.current
        const playerEl = player.element()

        // Melee blinks across the measured gap to Blue before swinging; ranged fires from range.
        let approachPx: number | undefined
        if (def?.attack.kind === 'melee' && playerEl) {
          const gap = anchor(handle.element()).x - anchor(playerEl).x
          approachPx = Math.max(0, gap - 128)
        }

        await handle.attack({ approachPx, resolveAt: 'complete', recover: false })

        if (def?.attack.effect && layer && playerEl) {
          const effect = def.attack.effect
          const playback = effect.playback
          const bodyImpact = anchor(playerEl, 6, -4, 0.72, 0.52)
          const groundImpact = anchor(playerEl, 0, -2, 0.5, 0.95)
          const targetPoint =
            playback === 'projectile'
              ? bodyImpact
              : effect.placement === 'caster'
                ? anchor(handle.element(), 0, -2, 0.5, 0.5)
                : effect.anchor === 'feet'
                  ? groundImpact
                  : anchor(playerEl, 6, -4, 0.58, 0.52)
          const impactTo = playback === 'projectile' && effect.anchor === 'feet' ? groundImpact : undefined
          await monsterAttackEffect(effect)({
            layer,
            backLayer,
            from: anchor(handle.element(), -14, -6),
            to: targetPoint,
            impactTo,
            sizeScale: effect.placement === 'caster' ? def.metrics.scale : 1,
            targetFacing: effect.placement === 'caster' ? 'left' : 'right',
          })
        } else if (def?.attack.kind === 'projectile' && def.attack.sheet && layer && playerEl) {
          await spriteProjectile(def.attack.sheet, { flip: true })({
            layer,
            from: anchor(handle.element(), -14, -6),
            to: anchor(playerEl, 6, -4, 0.72, 0.52),
          })
        }

        applyDamage()
        if (lethal) await player.defeat()
        else await boundedAnimation(player.hurt(), 900)
        await recoverMonster()
      } finally {
        applyDamage()
        await recoverMonster()
        setActiveMonsterId(null)
      }
    },
    [anchor, effectBackLayerRef, effectLayerRef, monsterHandles, playerRef, rosterRef, setActiveMonsterId, setPlayerHp, storyWorldRef],
  )
}
