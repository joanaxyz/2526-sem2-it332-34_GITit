import { useEffect, useRef, useState } from 'react'

import { isMotionReduced } from '@/shared/battle/hooks/battleMotion'
import { readPreference, writePreference } from '@/shared/utils/persistentState'

const CLAIM_ANIMATION_MS = 1300
const STORAGE_KEY_PREFIX = 'chest-claims:'

/**
 * Tracks which progress-reward chest thresholds have never been celebrated
 * on this device, so the caller can play a one-shot claim animation exactly
 * once per chest instead of on every visit.
 *
 * Reward progress is credited on a separate run page (adventure/challenge),
 * so the story map almost always remounts fresh with chests already earned
 * rather than crossing a threshold while this component stays mounted. A
 * small localStorage baseline (via the shared `persistentState` preference
 * helpers) is what lets a first-time-seen earned chest still read as "just
 * claimed" on the next visit, while chests earned before this baseline
 * existed are seeded in silently rather than celebrated retroactively.
 */
export function useNewlyEarnedChestThresholds(
  chapterId: number,
  earnedThresholds: number[],
): Set<number> {
  const [justEarned, setJustEarned] = useState<Set<number>>(() => new Set())
  const timeoutsRef = useRef<Map<number, number>>(new Map())

  useEffect(
    () => () => {
      timeoutsRef.current.forEach((id) => window.clearTimeout(id))
      timeoutsRef.current.clear()
    },
    [],
  )

  useEffect(() => {
    const key = `${STORAGE_KEY_PREFIX}${chapterId}`
    const stored = readPreference<number[] | null>(key, null)
    const currentEarned = [...new Set(earnedThresholds)]

    if (stored === null) {
      writePreference(key, currentEarned)
      return
    }

    const newlyEarned = currentEarned.filter((threshold) => !stored.includes(threshold))
    if (!newlyEarned.length) return

    writePreference(key, currentEarned)
    if (isMotionReduced()) return

    setJustEarned((current) => new Set([...current, ...newlyEarned]))

    newlyEarned.forEach((threshold) => {
      const existing = timeoutsRef.current.get(threshold)
      if (existing) window.clearTimeout(existing)
      const id = window.setTimeout(() => {
        timeoutsRef.current.delete(threshold)
        setJustEarned((current) => {
          if (!current.has(threshold)) return current
          const next = new Set(current)
          next.delete(threshold)
          return next
        })
      }, CLAIM_ANIMATION_MS)
      timeoutsRef.current.set(threshold, id)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chapterId, earnedThresholds.join(',')])

  return justEarned
}
