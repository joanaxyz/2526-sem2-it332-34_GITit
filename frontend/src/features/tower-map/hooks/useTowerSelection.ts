import { create } from 'zustand'

import type {
  ChallengeLevelAccess,
  ChallengeSummary,
  CommandAdventureSummary,
  TomeSummary,
} from '@/features/challenges/types'

// The whole tower is a single selection surface: one interactable artifact is
// selected at a time. The storey rail shows its overview; the lower-left dock
// shows its action. A challenge artifact resolves to the preferred challenge
// level, so the selection carries the exact level chosen.
export type TowerSelection =
  | { kind: 'adventure'; storeyId: number; adventure: CommandAdventureSummary }
  | {
      kind: 'challenge'
      storeyId: number
      challengeIndex: number
      challenge: ChallengeSummary
      level: ChallengeLevelAccess
      locked: boolean
    }
  | { kind: 'tome'; storeyId: number; tome: TomeSummary }

type TowerSelectionState = {
  selected: TowerSelection | null
  select: (selection: TowerSelection) => void
  clear: () => void
}

export const useTowerSelection = create<TowerSelectionState>((set) => ({
  selected: null,
  select: (selection) => set({ selected: selection }),
  clear: () => set({ selected: null }),
}))

/** True when `selection` points at the same artifact target as the current store value. */
export function isSelected(current: TowerSelection | null, candidate: TowerSelection): boolean {
  if (!current || current.kind !== candidate.kind) return false
  if (current.kind === 'adventure' && candidate.kind === 'adventure') {
    return current.adventure.id === candidate.adventure.id
  }
  if (current.kind === 'challenge' && candidate.kind === 'challenge') {
    return current.level.id === candidate.level.id
  }
  if (current.kind === 'tome' && candidate.kind === 'tome') {
    return current.tome.id === candidate.tome.id
  }
  return false
}
