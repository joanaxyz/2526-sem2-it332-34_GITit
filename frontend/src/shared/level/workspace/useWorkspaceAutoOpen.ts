import { useState } from 'react'

import { hasSeenLevelTour, markLevelTourSeen, type LevelTourMode } from '@/shared/level/utils/levelTour'
import { hasSeenTierStory, markTierStorySeen } from '@/shared/level/utils/tierStorySeen'

/**
 * The overlays that open on their own when a level starts, queued so they
 * never stack: the level story first, then the first-run workspace tour, then
 * the command guide. Each is derived from what is still unseen, so closing one
 * hands over to the next on the following render.
 *
 * The Story button can reopen the story at any time; that does not change the
 * seen flag and briefly holds the tour and guide back while it is open.
 */
export function useWorkspaceAutoOpen({
  userId,
  storyLevelKey,
  difficulty,
  tourMode,
  started,
}: {
  userId: number | null | undefined
  /** The level the story belongs to: an adventure level id, or `challenge:<trial id>`. */
  storyLevelKey: number | string | undefined
  difficulty: string | undefined
  tourMode: LevelTourMode
  /** Only a run in progress auto-opens anything. */
  started: boolean
}) {
  const storyKey = storyLevelKey !== undefined && difficulty ? `${storyLevelKey}:${difficulty}` : null
  const tourKey = `${userId ?? 'guest'}:${tourMode}`
  const [dismissedStoryKey, setDismissedStoryKey] = useState<string | null>(null)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const [storyRequested, setStoryRequested] = useState(false)

  const storyPending = Boolean(
    started &&
      storyKey &&
      dismissedStoryKey !== storyKey &&
      !hasSeenTierStory(userId, storyLevelKey!, difficulty!),
  )
  const tourPending = started && dismissedTourKey !== tourKey && !hasSeenLevelTour(userId, tourMode)

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
        markTierStorySeen(userId, storyLevelKey!, difficulty!)
        setDismissedStoryKey(storyKey)
      }
      setStoryRequested(false)
    },
    closeTour: () => {
      markLevelTourSeen(userId, tourMode)
      setDismissedTourKey(tourKey)
    },
  }
}
