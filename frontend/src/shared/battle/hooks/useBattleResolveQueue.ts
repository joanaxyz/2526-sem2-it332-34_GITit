import { useCallback } from 'react'
import type { MutableRefObject } from 'react'

import { activeBattleMonsters } from '@/shared/battle/deriveBattleEvents'
import { missedAttackForCompanion } from '@/shared/battle/effects/effectRegistry'
import type { BattleQueue } from '@/shared/battle/battleQueue'
import type { BattleBackdropHandle } from '@/shared/battle/components/BattleBackdrop'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { BattleBlock, BattleMonster } from '@/shared/battle/types'
import { playWaveTransitionSound } from '@/shared/audio/battleAudio'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

import { prefersReducedMotion, TRAVEL_SCROLL_MS, TRAVEL_SCROLL_PX, wait } from './battleMotion'
import { battleResolveFlags, visibleRosterForResolve, visibleWaveRoster } from './battleResolveSnapshots'
import { useMonsterCounterattack } from './useMonsterCounterattack'
import { usePlayerAttackChoreography } from './usePlayerAttackChoreography'
import type { BattleTransitionCueConfig } from './battleDirectorTypes'

type Point = { x: number; y: number }

type BattleResolveQueueDeps = {
  queue: BattleQueue
  rosterRef: MutableRefObject<BattleMonster[]>
  playerRef: MutableRefObject<PlayerActorHandle | null>
  backdropRef: MutableRefObject<BattleBackdropHandle | null>
  effectLayerRef: MutableRefObject<HTMLDivElement | null>
  effectBackLayerRef: MutableRefObject<HTMLDivElement | null>
  monsterHandles: MutableRefObject<Map<number, MonsterActorHandle>>
  storyWorldRef: MutableRefObject<StoryWorldDef>
  companionSlugRef: MutableRefObject<string>
  attackPendingRef: MutableRefObject<boolean>
  defeatedRef: MutableRefObject<boolean>
  anchor: (el: Element | null, dx?: number, dy?: number, xFrac?: number, yFrac?: number) => Point
  monsterImpactAnchor: (monsterId: number, side?: 'left' | 'right') => Point
  monsterFeetAnchor: (monsterId: number) => Point
  monsterSizeScale: (monsterId: number) => number
  missedSpellGroundAnchor: (playerEl: Element | null, enemyEl: Element | null) => Point
  playApproach: (next: BattleMonster[], fromEdge?: boolean, fast?: boolean) => Promise<void>
  playCenterBeat: (fast?: boolean) => Promise<void>
  emitTransitionCue: (cue: BattleTransitionCueConfig) => void
  setDefeated: (next: boolean) => void
  setActiveMonsterId: (next: number | null) => void
  setEntranceHidden: (monsters: BattleMonster[], hidden: boolean) => void
  bumpRosterEpoch: () => void
  setMonster: (id: number, patch: Partial<BattleMonster>) => void
  setPlayerHp: (next: number | null) => void
  setPlayerMaxHp: (next: number | null) => void
  setRoster: (updater: (prev: BattleMonster[]) => BattleMonster[]) => void
}

/**
 * Owns command-resolution choreography: player attacks, monster damage/deaths,
 * monster counterattacks, wave swaps, and final roster/HP snap state. Keeping
 * this queue writer out of `useBattleDirector` leaves that hook as orchestration
 * instead of a 1k-line animation script.
 */
export function useBattleResolveQueue({
  queue,
  rosterRef,
  playerRef,
  backdropRef,
  effectLayerRef,
  effectBackLayerRef,
  monsterHandles,
  storyWorldRef,
  companionSlugRef,
  attackPendingRef,
  defeatedRef,
  anchor,
  monsterImpactAnchor,
  monsterFeetAnchor,
  monsterSizeScale,
  missedSpellGroundAnchor,
  playApproach,
  playCenterBeat,
  emitTransitionCue,
  setDefeated,
  setActiveMonsterId,
  setEntranceHidden,
  bumpRosterEpoch,
  setMonster,
  setPlayerHp,
  setPlayerMaxHp,
  setRoster,
}: BattleResolveQueueDeps) {
  const strikePlayer = useMonsterCounterattack({
    rosterRef,
    playerRef,
    effectLayerRef,
    effectBackLayerRef,
    monsterHandles,
    storyWorldRef,
    anchor,
    setActiveMonsterId,
    setPlayerHp,
  })

  const playPlayerAttack = usePlayerAttackChoreography({
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
  })

  const onResolve = useCallback(
    (block: BattleBlock) => {
      const reduced = prefersReducedMotion()
      const hadAttack = attackPendingRef.current
      attackPendingRef.current = false
      const events = block.events
      const {
        hasPlayerAttack,
        hasMonsterAttack,
        hasPlayerDefeat,
      } = battleResolveFlags(block)

      if (typeof block.player_max_hp === 'number') setPlayerMaxHp(block.player_max_hp)
      if (typeof block.player_hp === 'number' && !hasMonsterAttack) setPlayerHp(block.player_hp)
      setRoster((prev) => visibleRosterForResolve(block, prev))
      if (hadAttack && events.length === 0) playerRef.current?.cancelAttack()

      // Real attacks (including misses, which now cast for real) clear their pose
      // inside each player_attack beat below; a turn with no player attack at all
      // just clears the lingering windup here.
      queue.enqueue({
        run: (ctx) => {
          const player = playerRef.current
          if (!player || !hadAttack) return
          if (ctx.fast || reduced || !hasPlayerAttack) player.cancelAttack()
        },
      })

      for (const event of events) {
        switch (event.type) {
          case 'player_attack': {
            queue.enqueue({
              run: async (ctx) => {
                await playPlayerAttack(event, !ctx.fast && !reduced)
              },
            })
            if (event.missed) {
              // The spell connected but did nothing: after the companion's miss
              // release, the effect fizzles off the target and lands on the open
              // floor between the fighters before the monster counter-turn.
              queue.enqueue({
                run: async (ctx) => {
                  if (ctx.fast || reduced) return
                  const player = playerRef.current
                  const layer = effectLayerRef.current
                  const target = rosterRef.current.find((m) => m.id === event.target)
                  const targetEl = target ? monsterHandles.current.get(target.id)?.element() : null
                  if (!player || !layer || !targetEl) return
                  await missedAttackForCompanion(companionSlugRef.current)({
                    layer,
                    from: monsterImpactAnchor(event.target),
                    to: missedSpellGroundAnchor(player.element(), targetEl),
                  })
                },
              })
            }
            break
          }
          case 'monster_death': {
            queue.enqueue({
              run: async (ctx) => {
                if (!ctx.fast && !reduced) {
                  await monsterHandles.current.get(event.monster)?.die()
                }
                setMonster(event.monster, { hp: 0, alive: false })
              },
            })
            break
          }
          case 'monster_attack': {
            // The strike that ends the run plays Blue's death at impact instead
            // of a hurt flinch; the player_defeat beat then holds the corpse.
            const lethal =
              hasPlayerDefeat && event === events.filter((candidate) => candidate.type === 'monster_attack').at(-1)
            queue.enqueue({
              run: async (ctx) => {
                await strikePlayer(event.monster, event.player_hp_after, !ctx.fast && !reduced, lethal)
              },
            })
            break
          }
          case 'wave_cleared': {
            queue.enqueue({
              cosmetic: true,
              run: async (ctx) => {
                if (ctx.fast || reduced) return
                playWaveTransitionSound()
                emitTransitionCue({ wave: event.next_wave + 1, total: block.waves.length })
                // Blue visibly lags behind the faster world pan as he runs back
                // to the left edge; he never disappears between waves.
                await Promise.all([
                  playerRef.current?.travelBack() ?? Promise.resolve(),
                  backdropRef.current?.scroll(TRAVEL_SCROLL_PX, TRAVEL_SCROLL_MS) ?? Promise.resolve(),
                ])
              },
            })
            queue.enqueue({
              run: (ctx) => {
                // Keep the snap state visible if this wave's entrance is
                // fast-forwarded.
                if (ctx.fast) playerRef.current?.reset(true)
                const nextWave = visibleWaveRoster(block, event.next_wave)
                setEntranceHidden(nextWave, !ctx.fast && !reduced)
                bumpRosterEpoch()
                setRoster(() => nextWave)
              },
            })
            queue.enqueue({
              run: async (ctx) => {
                const nextWave = block.waves[event.next_wave]?.monsters ?? []
                await playApproach(nextWave, true, ctx.fast)
              },
            })
            queue.enqueue({
              run: async (ctx) => {
                try {
                  await playCenterBeat(ctx.fast)
                } finally {
                  setEntranceHidden([], false)
                }
              },
            })
            break
          }
          case 'encounter_cleared': {
            queue.enqueue({
              cosmetic: true,
              run: () => wait(reduced ? 0 : 120),
            })
            break
          }
          case 'player_defeat': {
            queue.enqueue({
              run: async (ctx) => {
                defeatedRef.current = true
                if (!ctx.fast && !reduced) {
                  await playerRef.current?.defeat()
                } else {
                  void playerRef.current?.defeat()
                }
                setDefeated(true)
              },
            })
            break
          }
        }
      }

      queue.enqueue({
        run: () => {
          if (typeof block.player_max_hp === 'number') setPlayerMaxHp(block.player_max_hp)
          if (typeof block.player_hp === 'number') setPlayerHp(block.player_hp)
          if (!hasPlayerDefeat) playerRef.current?.cancelAttack()
          setRoster(() => activeBattleMonsters(block).map((monster) => ({ ...monster })))
        },
      })
    },
    [
      backdropRef,
      bumpRosterEpoch,
      attackPendingRef,
      companionSlugRef,
      defeatedRef,
      effectLayerRef,
      emitTransitionCue,
      missedSpellGroundAnchor,
      monsterHandles,
      monsterImpactAnchor,
      playApproach,
      playCenterBeat,
      playerRef,
      queue,
      rosterRef,
      setDefeated,
      setEntranceHidden,
      setPlayerHp,
      setPlayerMaxHp,
      setRoster,
      setMonster,
      playPlayerAttack,
      strikePlayer,
    ],
  )

  return { onResolve }
}
