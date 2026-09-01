import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { useBattleRosterState } from '@/shared/battle/hooks/useBattleRosterState'

describe('useBattleRosterState player vitals', () => {
  it('lets HP drain but never climb inside an encounter', () => {
    const { result } = renderHook(() => useBattleRosterState())

    act(() => result.current.resetPlayerVitals(4, 4))
    expect(result.current.playerHp).toBe(4)

    act(() => result.current.setPlayerHp(3))
    expect(result.current.playerHp).toBe(3)

    // The wave-clearing command's payload already reports the next wave's full
    // budget; honouring it here refilled the bar mid-fight.
    act(() => result.current.setPlayerHp(4))
    expect(result.current.playerHp).toBe(3)
  })

  it('refills only when a new encounter is staged', () => {
    const { result } = renderHook(() => useBattleRosterState())

    act(() => result.current.resetPlayerVitals(4, 4))
    act(() => result.current.setPlayerHp(1))
    expect(result.current.playerHp).toBe(1)

    act(() => result.current.resetPlayerVitals(6, 6))
    expect(result.current.playerHp).toBe(6)
    expect(result.current.playerMaxHp).toBe(6)
  })

  it('adopts a first or cleared value verbatim', () => {
    const { result } = renderHook(() => useBattleRosterState())

    act(() => result.current.setPlayerHp(5))
    expect(result.current.playerHp).toBe(5)

    act(() => result.current.setPlayerHp(null))
    expect(result.current.playerHp).toBeNull()
  })
})
