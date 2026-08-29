import { useCallback } from 'react'
import type { MutableRefObject } from 'react'

import type { BattleQueue } from '@/shared/battle/battleQueue'
import type { BattleBackdropHandle } from '@/shared/battle/components/BattleBackdrop'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { BattleMonster } from '@/shared/battle/types'

import {
  CAMERA_FOLLOW_FRAC,
  CENTER_SCROLL_MS,
  MONSTER_ENTRY_STAGGER_MS,
  MONSTER_PEEK_MS,
  nextPaint,
  PEEK_START_FRAC,
  prefersReducedMotion,
  RUN_IN_SCROLL_MIN_PX,
  RUN_IN_SCROLL_SCALE,
  SIGHTED_IDLE_PAUSE_MS,
  TRAVEL_SCROLL_MS,
  TRAVEL_SCROLL_PX,
  wait,
} from './battleMotion'
import type { BattleTransitionCueConfig, EncounterOptions } from './battleDirectorTypes'

type EncounterChoreographyDeps = {
  queue: BattleQueue
  rosterRef: MutableRefObject<BattleMonster[]>
  playerRef: MutableRefObject<PlayerActorHandle | null>
  backdropRef: MutableRefObject<BattleBackdropHandle | null>
  monsterHandles: MutableRefObject<Map<number, MonsterActorHandle>>
  measureWideFrame: () => { monsterEntryFromPx: number; monsterPeekPx: number }
  measureClosureRun: () => { blueClosurePx: number }
  centerScrollPx: () => number
  panCamera: (px: number, ms: number) => Promise<void>
  resetCamera: (ms: number) => Promise<void>
  emitTransitionCue: (cue: BattleTransitionCueConfig) => void
  setDefeated: (next: boolean) => void
  setActiveMonsterId: (next: number | null) => void
  setPlayerHp: (next: number | null) => void
  setPlayerMaxHp: (next: number | null) => void
  setEntranceHidden: (monsters: BattleMonster[], hidden: boolean) => void
  bumpRosterEpoch: () => void
  setRoster: (updater: (prev: BattleMonster[]) => BattleMonster[]) => void
  defeatedRef: MutableRefObject<boolean>
}

export function useBattleEncounterChoreography({
  queue,
  rosterRef,
  playerRef,
  backdropRef,
  monsterHandles,
  measureWideFrame,
  measureClosureRun,
  centerScrollPx,
  panCamera,
  resetCamera,
  emitTransitionCue,
  setDefeated,
  setActiveMonsterId,
  setPlayerHp,
  setPlayerMaxHp,
  setEntranceHidden,
  bumpRosterEpoch,
  setRoster,
  defeatedRef,
}: EncounterChoreographyDeps) {
  /**
   * Run-in approach shared by encounter entry and wave swaps: Blue runs at the
   * left edge while the parallax pans, the foe peeks from the right rim, then
   * Blue closes range on foot and settles to idle. `playCenterBeat` recentres
   * the duel afterwards.
   */
  const playApproach = useCallback(
    async (next: BattleMonster[], fromEdge = false, fast = false) => {
      if (fast || prefersReducedMotion()) {
        await Promise.all(next.map((m) => monsterHandles.current.get(m.id)?.walkIn(0, 0, 0) ?? Promise.resolve()))
        playerRef.current?.reset(true)
        return
      }

      await nextPaint()
      // Measure while the actor is still at the centred duel slot (translate 0).
      for (const m of next) {
        const node = monsterHandles.current.get(m.id)?.element()
        if (node) node.style.transform = 'translateX(0)'
      }
      const wide = measureWideFrame()
      for (const m of next) {
        monsterHandles.current.get(m.id)?.prepOffscreen(wide.monsterEntryFromPx)
      }

      const peekMonsters = (delay = 0) =>
        Promise.all(
          next.map((m, i) =>
            new Promise<void>((resolve) => {
              window.setTimeout(() => {
                const handle = monsterHandles.current.get(m.id)
                if (handle) {
                  void handle
                    .walkIn(
                      wide.monsterEntryFromPx + i * 36,
                      MONSTER_PEEK_MS,
                      wide.monsterPeekPx + i * 18,
                    )
                    .then(resolve)
                } else resolve()
              }, delay + i * MONSTER_ENTRY_STAGGER_MS)
            }),
          ),
        )

      // Blue runs in place at the edge while the world pans beneath him.
      playerRef.current?.holdTravel(TRAVEL_SCROLL_MS)
      if (fromEdge) {
        // Travel pan already played (travelBack rode it); the foe just peeks.
        await peekMonsters()
      } else {
        await Promise.all([
          backdropRef.current?.scroll(TRAVEL_SCROLL_PX, TRAVEL_SCROLL_MS) ?? Promise.resolve(),
          wait(Math.round(TRAVEL_SCROLL_MS * PEEK_START_FRAC)).then(() => peekMonsters()),
        ])
      }
      // Foe sighted at the rim: Blue closes range, then idles at the duel.
      await wait(SIGHTED_IDLE_PAUSE_MS)
      const { blueClosurePx } = measureClosureRun()
      const closureScrollPx = Math.max(RUN_IN_SCROLL_MIN_PX, Math.abs(blueClosurePx) * RUN_IN_SCROLL_SCALE)
      await Promise.all([
        playerRef.current?.runIn(blueClosurePx) ?? Promise.resolve(),
        backdropRef.current?.scroll(closureScrollPx, TRAVEL_SCROLL_MS) ?? Promise.resolve(),
        // Camera follows Blue as he runs: it drifts opposite his advance so he
        // stays more centred while the world (and foe) sweeps past. resetCamera
        // at the centre beat eases it back to the duel framing.
        panCamera(-blueClosurePx * CAMERA_FOLLOW_FRAC, TRAVEL_SCROLL_MS),
      ])
    },
    [backdropRef, measureClosureRun, measureWideFrame, monsterHandles, panCamera, playerRef],
  )

  /** Camera lock: ease actors into the centred duel lane. */
  const playCenterBeat = useCallback(
    async (fast = false) => {
      const living = rosterRef.current
      if (fast || prefersReducedMotion()) {
        await Promise.all([
          ...living.map((m) => monsterHandles.current.get(m.id)?.slideTo(0, 0) ?? Promise.resolve()),
          playerRef.current?.slideTo(0, 0) ?? Promise.resolve(),
        ])
        void resetCamera(0)
        playerRef.current?.reset(true)
        return
      }
      const scrollPx = centerScrollPx()
      await Promise.all([
        playerRef.current?.slideTo(0, CENTER_SCROLL_MS) ?? Promise.resolve(),
        ...living.map((m) => monsterHandles.current.get(m.id)?.slideTo(0, CENTER_SCROLL_MS) ?? Promise.resolve()),
        backdropRef.current?.scroll(scrollPx, CENTER_SCROLL_MS) ?? Promise.resolve(),
        resetCamera(CENTER_SCROLL_MS),
      ])
    },
    [backdropRef, centerScrollPx, monsterHandles, playerRef, resetCamera, rosterRef],
  )

  const setEncounter = useCallback(
    (next: BattleMonster[], opts?: EncounterOptions) => {
      const reduced = prefersReducedMotion()
      const entry = opts?.entry ?? 'run'
      const travelsBackToEdge = Boolean(opts?.travel && entry === 'run' && !reduced)
      const cue = opts?.transitionCue ?? null

      // Departure: the previous encounter cleared - Blue runs back to the edge.
      // The world pan rides the arrival's travel, not the exit.
      if (opts?.travel) {
        queue.enqueue({
          cosmetic: true,
          run: async () => {
            if (reduced) return
            if (cue) emitTransitionCue(cue)
            await Promise.all([
              playerRef.current?.travelBack() ?? Promise.resolve(),
              backdropRef.current?.scroll(TRAVEL_SCROLL_PX, TRAVEL_SCROLL_MS) ?? Promise.resolve(),
            ])
          },
        })
      }

      queue.enqueue({
        run: (ctx) => {
          // Un-dim here (not synchronously) so a defeat beat queued just before
          // the next encounter gets its moment first. Leave Blue at a visible
          // idle pose as the safe snap state.
          defeatedRef.current = false
          if (!travelsBackToEdge || ctx.fast) playerRef.current?.reset(true)
          setDefeated(false)
          setActiveMonsterId(null)
          setPlayerHp(typeof opts?.playerHp === 'number' ? opts.playerHp : null)
          setPlayerMaxHp(typeof opts?.playerMaxHp === 'number' ? opts.playerMaxHp : null)
          setEntranceHidden(next, entry !== 'none' && !ctx.fast && !reduced)
          bumpRosterEpoch()
          setRoster(() => next.map((m) => ({ ...m })))
        },
      })

      // Arrival: run at the edge while the world pans, close range, then the
      // camera lock. Snap steps so the intro is never dropped by the cosmetic
      // timeout.
      queue.enqueue({
        run: async (ctx) => {
          if (entry === 'none') return
          if (!travelsBackToEdge && !ctx.fast && !reduced && cue) emitTransitionCue(cue)
          await playApproach(next, travelsBackToEdge, ctx.fast || reduced)
        },
      })
      queue.enqueue({
        run: async (ctx) => {
          if (entry === 'none') return
          try {
            await playCenterBeat(ctx.fast || reduced)
          } finally {
            setEntranceHidden([], false)
          }
        },
      })
    },
    [
      backdropRef,
      bumpRosterEpoch,
      defeatedRef,
      emitTransitionCue,
      playApproach,
      playCenterBeat,
      playerRef,
      queue,
      setActiveMonsterId,
      setDefeated,
      setEntranceHidden,
      setPlayerHp,
      setPlayerMaxHp,
      setRoster,
    ],
  )

  return { playApproach, playCenterBeat, setEncounter }
}
