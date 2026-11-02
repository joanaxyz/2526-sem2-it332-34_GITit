import { useCallback, useEffect, useState } from 'react'

import {
  hasSeenChapterNavCoachmark,
  markChapterNavCoachmarkSeen,
  hasSeenWorldMascotCoachmark,
  markWorldMascotCoachmarkSeen,
} from '@/shared/level/utils/milestones'

export function useStoryMapCoachmarks({
  userId,
  orientationRequested,
  mascotSuppressed,
  hasCompanion,
  loadoutLoading,
}: {
  userId?: number
  orientationRequested: boolean
  mascotSuppressed: boolean
  hasCompanion: boolean
  loadoutLoading: boolean
}) {
  const [chapterCoachmarkVisible, setChapterCoachmarkVisible] = useState(false)
  const [worldMascotCoachmarkVisible, setWorldMascotCoachmarkVisible] = useState(false)

  useEffect(() => {
    if (!orientationRequested || hasSeenChapterNavCoachmark(userId)) return
    const timer = setTimeout(() => setChapterCoachmarkVisible(true), 800)
    return () => clearTimeout(timer)
  }, [orientationRequested, userId])

  useEffect(() => {
    if (mascotSuppressed || !hasCompanion || loadoutLoading || hasSeenWorldMascotCoachmark(userId)) return
    const timer = setTimeout(() => setWorldMascotCoachmarkVisible(true), 1000)
    return () => clearTimeout(timer)
  }, [mascotSuppressed, hasCompanion, loadoutLoading, userId])

  const dismissChapterCoachmark = useCallback(() => {
    markChapterNavCoachmarkSeen(userId)
    setChapterCoachmarkVisible(false)
  }, [userId])

  const dismissWorldMascotCoachmark = useCallback(() => {
    markWorldMascotCoachmarkSeen(userId)
    setWorldMascotCoachmarkVisible(false)
  }, [userId])

  return {
    chapterCoachmarkVisible,
    dismissChapterCoachmark,
    worldMascotCoachmarkVisible,
    dismissWorldMascotCoachmark,
  }
}
