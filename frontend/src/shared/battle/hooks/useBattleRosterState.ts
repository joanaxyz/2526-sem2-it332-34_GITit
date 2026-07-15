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

  const setPlayerHp = useCallback((next: number | null) => {
    setPlayerHpState(next)
  }, [])

  const setPlayerMaxHp = useCallback((next: number | null) => {
    setPlayerMaxHpState(next)
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
    setRoster,
  }
}
