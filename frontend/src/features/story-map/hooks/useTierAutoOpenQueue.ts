import { useState } from 'react'

import type { TierDifficulty } from '@/features/story-map/components/tierWorkspaceTypes'
import { hasSeenTierStory, markTierStorySeen } from '@/features/story-map/utils/tierStorySeen'
import { hasSeenLevelTour, markLevelTourSeen } from '@/shared/level/utils/levelTour'

/**
 * The overlays that open on their own when a tier level starts, queued so they
 * never stack: the level story first, then the first-run workspace tour, then
 * the command guide. Each is derived from what is still unseen, so closing one
 * hands over to the next on the following render.
 *
 * The Story button can reopen the story at any time; that does not change the
 * seen flag and briefly holds the tour and guide back while it is open.
 */
export function useTierAutoOpenQueue({
  userId,
  adventureLevelId,
  difficulty,
  started,
}: {
  userId: number | null | undefined
  adventureLevelId: number | undefined
  difficulty: TierDifficulty | undefined
  /** Only a run in progress auto-opens anything. */
  started: boolean
}) {
  const storyKey = adventureLevelId !== undefined && difficulty ? `${adventureLevelId}:${difficulty}` : null
  const tourKey = `${userId ?? 'guest'}:tier`
  const [dismissedStoryKey, setDismissedStoryKey] = useState<string | null>(null)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const [storyRequested, setStoryRequested] = useState(false)

  const storyPending = Boolean(
    started &&
      storyKey &&
      dismissedStoryKey !== storyKey &&
      !hasSeenTierStory(userId, adventureLevelId!, difficulty!),
  )
  const tourPending = started && dismissedTourKey !== tourKey && !hasSeenLevelTour(userId, 'tier')

  const storyOpen = storyRequested || storyPending
  const tourOpen = !storyOpen && tourPending

  return {
    storyOpen,
    tourOpen,
    /** The command guide may open only once nothing ahead of it is showing. */
    guideAllowed: !storyOpen && !tourOpen,
    openStory: () => setStoryRequested(true),
    closeStory: () => {
      if (storyKey) {
        markTierStorySeen(userId, adventureLevelId!, difficulty!)
        setDismissedStoryKey(storyKey)
      }
      setStoryRequested(false)
    },
    closeTour: () => {
      markLevelTourSeen(userId, 'tier')
      setDismissedTourKey(tourKey)
    },
  }
}
