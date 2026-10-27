import { useCallback, useEffect, useRef } from 'react'

import { playStarRewardSound, preloadStarRewardSounds } from '@/shared/audio/battleAudio'

// The sprite timing stays here alongside its animation-driven sound cues.
export const STAR_REVEAL_DELAY_MS = 180
export const STAR_REVEAL_STAGGER_MS = 260

export function useStarRewardAudio(stars: number, ready: boolean): (grade: number) => void {
  const stopSounds = useRef<Array<() => void>>([])
  const playedGrades = useRef(new Set<number>())
  const suspended = useRef(false)
  const playCue = useCallback((grade: number) => {
    if (!ready || suspended.current || document.hidden || playedGrades.current.has(grade)) return
    playedGrades.current.add(grade)
    stopSounds.current.push(playStarRewardSound(grade))
  }, [ready])

  useEffect(() => {
    preloadStarRewardSounds(stars)
  }, [stars])

  useEffect(() => {
    if (!ready) return
    suspended.current = document.hidden
    const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    // Reduced motion has no animation events: acknowledge the final grade once.
    const timer = reducedMotion ? window.setTimeout(() => playCue(stars), 0) : undefined
    const stop = () => {
      suspended.current = true
      window.clearTimeout(timer)
      stopSounds.current.forEach(stopSound => stopSound())
      stopSounds.current.length = 0
    }
    const onVisibilityChange = () => { if (document.hidden) stop() }
    document.addEventListener('visibilitychange', onVisibilityChange)
    return () => {
      stop()
      document.removeEventListener('visibilitychange', onVisibilityChange)
    }
  }, [ready, stars, playCue])

  return playCue
}
