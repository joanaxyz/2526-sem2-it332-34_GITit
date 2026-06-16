import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { BattleQueue } from '@/shared/battle/battleQueue'
import { effectForSkill, fizzle, spriteProjectile } from '@/shared/battle/effects/effectRegistry'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleBlock, BattleMonster } from '@/shared/battle/types'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { TowerBackdropHandle } from '@/shared/battle/components/TowerBackdrop'
import type { TowerCrystalHandle } from '@/shared/battle/components/TowerCrystal'

export type EncounterOptions = {
  /** Blue flies up to the next floor before the new encounter stages in. */
  travel?: boolean
}

export type BattleDirector = {
  /** Current roster - render one MonsterActor per entry. */
  roster: BattleMonster[]
  defeated: boolean
  /** Callback refs the TowerBattleStage wires up (functions, not ref objects, so
   *  they are safe to pass during render). */
  bindPlayer: (handle: PlayerActorHandle | null) => void
  bindBackdrop: (handle: TowerBackdropHandle | null) => void
  bindCrystal: (handle: TowerCrystalHandle | null) => void
  bindEffectLayer: (node: HTMLDivElement | null) => void
  bindMonster: (id: number, handle: MonsterActorHandle | null) => void
  /** Latest roster snapshot (for deriveBattleEvents inputs). */
  currentMonsters: () => BattleMonster[]
  /** Command lifecycle. */
  onCastStart: () => void
  onResolve: (block: BattleBlock) => void
  onError: () => void
  /** Swap to a new encounter (level advance / initial mount / retry). */
  setEncounter: (roster: BattleMonster[], opts?: EncounterOptions) => void
}

function prefersReducedMotion(): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Translates command-lifecycle calls into sequential stage choreography. In the
 * tower-defense loop the player guards a crystal: a counted command casts at the
 * monsters; a miss lets a monster strike the crystal (pure drama - the cost was
 * the mana); running the mana dry shatters the crystal (defeat). Clearing a
 * level flies Blue up to the next floor.
 *
 * All per-frame work happens through imperative handles; React state changes are
 * limited to roster/HP snapshots (<2 per command).
 */
export function useBattleDirector(): BattleDirector {
  const [roster, setRosterState] = useState<BattleMonster[]>([])
  const [defeated, setDefeated] = useState(false)
  const rosterRef = useRef<BattleMonster[]>([])

  const playerRef = useRef<PlayerActorHandle | null>(null)
  const backdropRef = useRef<TowerBackdropHandle | null>(null)
  const crystalRef = useRef<TowerCrystalHandle | null>(null)
  const effectLayerRef = useRef<HTMLDivElement | null>(null)
  const monsterHandles = useRef(new Map<number, MonsterActorHandle>())
  const queue = useMemo(() => new BattleQueue(), [])
  const castPendingRef = useRef(false)
  const defeatedRef = useRef(false)

  useEffect(() => () => queue.dispose(), [queue])

  /** Single writer keeps the render state and the snapshot ref in lockstep. */
  const setRoster = useCallback((updater: (prev: BattleMonster[]) => BattleMonster[]) => {
    setRosterState((prev) => {
      const next = updater(prev)
      rosterRef.current = next
      return next
    })
  }, [])

  const bindPlayer = useCallback((handle: PlayerActorHandle | null) => {
    playerRef.current = handle
  }, [])
  const bindBackdrop = useCallback((handle: TowerBackdropHandle | null) => {
    backdropRef.current = handle
  }, [])
  const bindCrystal = useCallback((handle: TowerCrystalHandle | null) => {
    crystalRef.current = handle
  }, [])
  const bindEffectLayer = useCallback((node: HTMLDivElement | null) => {
    effectLayerRef.current = node
  }, [])
  const bindMonster = useCallback((id: number, handle: MonsterActorHandle | null) => {
    if (handle) monsterHandles.current.set(id, handle)
    else monsterHandles.current.delete(id)
  }, [])

  /** Layer-local center of an element, for effect launch/impact points. */
  const anchor = useCallback((el: Element | null, dx = 0, dy = 0) => {
    const layer = effectLayerRef.current
    if (!layer || !el) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    const box = el.getBoundingClientRect()
    return {
      x: box.left + box.width / 2 - layerBox.left + dx,
      y: box.top + box.height / 2 - layerBox.top + dy,
    }
  }, [])

  const setMonster = useCallback(
    (id: number, patch: Partial<BattleMonster>) => {
      setRoster((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)))
    },
    [setRoster],
  )

  /**
   * One monster besieges the crystal: attack/lunge strip, then (ranged) a
   * projectile toward the crystal, then the crystal jolts. Shared by the miss
   * event and the ambient siege loop. Purely cosmetic - never touches state.
   */
  const strikeCrystal = useCallback(
    async (monsterId: number) => {
      const handle = monsterHandles.current.get(monsterId)
      const crystal = crystalRef.current
      if (!handle || !crystal) return
      await handle.attack()
      const attacker = rosterRef.current.find((m) => m.id === monsterId)
      const def = attacker ? definitionForMonster(attacker) : null
      const layer = effectLayerRef.current
      const crystalEl = crystal.element()
      if (def?.attack.kind === 'projectile' && layer && crystalEl) {
        // Monster (left of the crystal) looses rightward at it; the source sheet
        // already faces right, so no flip.
        await spriteProjectile(def.attack.sheet)({
          layer,
          from: anchor(handle.element(), 14, -6),
          to: anchor(crystalEl, -6, 0),
        })
      }
      await crystal.shake()
    },
    [anchor],
  )

  const onCastStart = useCallback(() => {
    if (defeatedRef.current) return
    castPendingRef.current = true
    if (queue.busy) queue.fastForward()
    // The cast sprite plays on resolve (idle -> cast -> idle), not on submit.
  }, [queue])

  const onError = useCallback(() => {
    castPendingRef.current = false
  }, [])

  const onResolve = useCallback(
    (block: BattleBlock) => {
      const reduced = prefersReducedMotion()
      const hadCast = castPendingRef.current
      castPendingRef.current = false
      const events = block.events
      const hasPlayerAttack = events.some((e) => e.type === 'player_attack')
      const hasMiss = events.some((e) => e.type === 'monster_attack')

      // Play the cast for the resolved outcome: idle -> cast -> idle, once.
      // Skipped on fast-forward / reduced motion (the state-snap steps below
      // still apply HP and deaths). A miss that drew a crystal strike gets a
      // fizzle so the spell visibly comes to nothing.
      queue.enqueue({
        run: async (ctx) => {
          const player = playerRef.current
          if (!player || !hadCast || ctx.fast || reduced) return
          if (!hasPlayerAttack && !hasMiss) return
          if (hasPlayerAttack) {
            await player.cast()
            return
          }
          // No progress: a brief miss beat + a fizzle toward the front monster.
          await player.miss()
          const layer = effectLayerRef.current
          const target = rosterRef.current.find((m) => m.alive)
          const targetEl = target ? monsterHandles.current.get(target.id)?.element() : null
          if (layer && targetEl) {
            await fizzle({ layer, from: anchor(player.element(), 26, -8), to: anchor(targetEl) })
          }
        },
      })

      for (const event of events) {
        switch (event.type) {
          case 'player_attack': {
            queue.enqueue({
              run: async (ctx) => {
                if (!ctx.fast && !reduced) {
                  const layer = effectLayerRef.current
                  const targetHandle = monsterHandles.current.get(event.target)
                  const targetEl = targetHandle?.element()
                  if (layer && targetEl) {
                    await effectForSkill(event.skill)({
                      layer,
                      from: anchor(playerRef.current?.element() ?? null, 26, -8),
                      to: anchor(targetEl),
                    })
                    void targetHandle?.hurt()
                  }
                }
                setMonster(event.target, { hp: event.target_hp_after })
              },
            })
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
            // A miss: the rear monster lunges at the crystal. Non-cosmetic so a
            // miss is never silently dropped on fast-forward - there we just
            // jolt the crystal; otherwise the full lunge + projectile + shake.
            queue.enqueue({
              run: async (ctx) => {
                if (reduced) return
                if (ctx.fast) {
                  void crystalRef.current?.shake()
                  return
                }
                await strikeCrystal(event.monster)
              },
            })
            break
          }
          case 'encounter_cleared': {
            queue.enqueue({
              cosmetic: true,
              run: () => new Promise<void>((resolve) => window.setTimeout(resolve, reduced ? 0 : 350)),
            })
            break
          }
          case 'player_defeat': {
            queue.enqueue({
              run: () => {
                defeatedRef.current = true
                crystalRef.current?.shatter()
                setDefeated(true)
              },
            })
            break
          }
        }
      }
    },
    [anchor, queue, setMonster, strikeCrystal],
  )

  /**
   * Ambient siege: between commands the living monsters keep harrying the
   * crystal so the floor reads as actively under attack rather than frozen.
   * Purely cosmetic - it never touches HP/roster/mana and fully yields to
   * command choreography, firing only while the queue is idle and the run is
   * live. Skipped under reduced motion and while the tab is hidden.
   */
  useEffect(() => {
    if (prefersReducedMotion()) return
    let timer = 0
    let stopped = false
    let inFlight = false

    const schedule = (ms: number) => {
      timer = window.setTimeout(tick, ms)
    }
    const tick = async () => {
      if (stopped) return
      const ready =
        !inFlight &&
        !queue.busy &&
        !castPendingRef.current &&
        !defeatedRef.current &&
        !document.hidden &&
        rosterRef.current.some((m) => m.alive)
      if (ready) {
        inFlight = true
        try {
          const alive = rosterRef.current.filter((m) => m.alive)
          const attacker = alive[Math.floor(Math.random() * alive.length)]
          await strikeCrystal(attacker.id)
        } catch {
          // A dropped flourish must never wedge the loop.
        } finally {
          inFlight = false
        }
      }
      if (!stopped) schedule(700 + Math.random() * 900)
    }
    schedule(1200)
    return () => {
      stopped = true
      window.clearTimeout(timer)
    }
  }, [queue, strikeCrystal])

  const setEncounter = useCallback(
    (next: BattleMonster[], opts?: EncounterOptions) => {
      const reduced = prefersReducedMotion()
      if (opts?.travel) {
        queue.enqueue({
          cosmetic: true,
          run: async () => {
            if (reduced) return
            // Blue takes off and rises a floor while the sky pans up.
            await Promise.all([
              playerRef.current?.liftOff() ?? Promise.resolve(),
              backdropRef.current?.climb(900) ?? Promise.resolve(),
            ])
          },
        })
      }
      queue.enqueue({
        run: () => {
          // Un-dim and restore the crystal here (not synchronously) so a defeat
          // beat queued just before the next encounter gets its moment first.
          defeatedRef.current = false
          crystalRef.current?.reset()
          setDefeated(false)
          setRoster(() => next.map((m) => ({ ...m })))
        },
      })
      queue.enqueue({
        cosmetic: true,
        run: async () => {
          if (reduced) return
          // Actors mount on the next frame; Blue descends onto the new floor (on
          // a level-up) or dashes in to lock range near the tower (encounter
          // start) as the monsters march in. The fight reads as starting once
          // Blue is in position.
          await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()))
          await Promise.all([
            opts?.travel
              ? (playerRef.current?.landIn() ?? Promise.resolve())
              : (playerRef.current?.runIn() ?? Promise.resolve()),
            ...next.map(
              (m, i) =>
                new Promise<void>((resolve) => {
                  window.setTimeout(() => {
                    const handle = monsterHandles.current.get(m.id)
                    if (handle) void handle.walkIn(140 + i * 50).then(resolve)
                    else resolve()
                  }, i * 160)
                }),
            ),
          ])
        },
      })
    },
    [queue, setRoster],
  )

  return {
    roster,
    defeated,
    bindPlayer,
    bindBackdrop,
    bindCrystal,
    bindEffectLayer,
    bindMonster,
    currentMonsters: useCallback(() => rosterRef.current, []),
    onCastStart,
    onResolve,
    onError,
    setEncounter,
  }
}
