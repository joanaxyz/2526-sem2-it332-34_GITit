import { useCallback, useRef, useState } from 'react'

import type { BattleMonster } from '@/shared/battle/types'

export function useBattleRosterState() {
  const [roster, setRosterState] = useState<BattleMonster[]>([])
  const [playerHp, setPlayerHpState] = useState<number | null>(null)
  const [playerMaxHp, setPlayerMaxHpState] = useState<number | null>(null)
  // Bumped every time the roster is *replaced* with a new set of monsters (new
  // encounter or new wave). Combined with the monster id into the actor's React
  // key, it forces a fresh MonsterActor per wave so a dead monster's held death
  // frame can never bleed onto the next wave's monster (which often reuses id 0).
  const [rosterEpoch, setRosterEpoch] = useState(0)
  const rosterRef = useRef<BattleMonster[]>([])

  const bumpRosterEpoch = useCallback(() => setRosterEpoch((epoch) => epoch + 1), [])

  /** Single writer keeps the render state and the snapshot ref in lockstep. */
  const setRoster = useCallback((updater: (prev: BattleMonster[]) => BattleMonster[]) => {
    setRosterState((prev) => {
      const next = updater(prev)
      rosterRef.current = next
      return next
    })
  }, [])

  const setMonster = useCallback(
    (id: number, patch: Partial<BattleMonster>) => {
      setRoster((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)))
    },
    [setRoster],
  )

  /**
   * Damage-only writer: HP never climbs while an encounter is on screen.
   * Command outcomes report the *absolute* remaining budget, and the payload for
   * a wave-clearing command already carries the next wave's untouched budget -
   * applying it verbatim refilled Blue's bar mid-fight, while the wave he just
   * cleared was still playing its death beat. Refills belong to encounter
   * staging, which owns the moment the next wave actually arrives.
   */
  const setPlayerHp = useCallback((next: number | null) => {
    setPlayerHpState((prev) => (prev === null || next === null ? next : Math.min(prev, next)))
  }, [])

  const setPlayerMaxHp = useCallback((next: number | null) => {
    setPlayerMaxHpState(next)
  }, [])

  /** Authoritative vitals for a newly staged encounter - the only refill path. */
  const resetPlayerVitals = useCallback((hp: number | null, maxHp: number | null) => {
    setPlayerHpState(hp)
    setPlayerMaxHpState(maxHp)
  }, [])

  const currentMonsters = useCallback(() => rosterRef.current, [])

  return {
    roster,
    rosterRef,
    rosterEpoch,
    playerHp,
    playerMaxHp,
    bumpRosterEpoch,
    currentMonsters,
    setMonster,
    setPlayerHp,
    setPlayerMaxHp,
    resetPlayerVitals,
    setRoster,
  }
}
