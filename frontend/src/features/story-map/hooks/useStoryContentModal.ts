import { create } from 'zustand'

import type { ChallengeSummary, AdventureSummary } from '@/features/challenges/types'

export type ContentModalTarget =
  | {
      kind: 'adventure'
      adventures: AdventureSummary[]
      locked?: boolean
      lockReason?: string
    }
  | {
      kind: 'challenge'
      chapterId: number
      challenges: ChallengeSummary[]
      locked: boolean
      lockReason?: string
    }

type StoryContentModalState = {
  active: ContentModalTarget | null
  open: (target: ContentModalTarget) => void
  close: () => void
  reset: () => void
}

export const useStoryContentModal = create<StoryContentModalState>((set) => ({
  active: null,
  open: (target) => set({ active: target }),
  close: () => set({ active: null }),
  reset: () => set({ active: null }),
}))
