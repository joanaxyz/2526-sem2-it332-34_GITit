import { renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'
import type { BattleMonster } from '@/shared/battle/types'

function monster(id: number): BattleMonster {
  return {
    id,
    species: 'bone-soldier',
    tier: 'mob',
    hp: 3,
    max_hp: 3,
    alive: true,
  }
}

function directorMock() {
  return {
    setStoryWorldSlug: vi.fn(),
    setEncounter: vi.fn(),
  } as unknown as BattleDirector
}

describe('useBattleEncounterSetup', () => {
  it('stages once per encounter identity and travels only after the first encounter', () => {
    const director = directorMock()
    const roster = [monster(1)]

    const { rerender } = renderHook(
      ({ encounterKey, playerHp }) =>
        useBattleEncounterSetup({
          director,
          storyWorldSlug: 'arcane-spire',
          encounterKey,
          roster,
          travelOnEncounterChange: true,
          playerHp,
          playerMaxHp: 5,
        }),
      { initialProps: { encounterKey: 'wave-1', playerHp: 5 } },
    )

    expect(director.setEncounter).toHaveBeenCalledTimes(1)
    expect(director.setEncounter).toHaveBeenLastCalledWith(
      roster,
      expect.objectContaining({ travel: false, playerHp: 5, playerMaxHp: 5 }),
    )

    rerender({ encounterKey: 'wave-1', playerHp: 4 })
    expect(director.setEncounter).toHaveBeenCalledTimes(1)

    rerender({ encounterKey: 'wave-2', playerHp: 4 })
    expect(director.setEncounter).toHaveBeenCalledTimes(2)
    expect(director.setEncounter).toHaveBeenLastCalledWith(
      roster,
      expect.objectContaining({ travel: true, playerHp: 4, playerMaxHp: 5 }),
    )
  })
})

