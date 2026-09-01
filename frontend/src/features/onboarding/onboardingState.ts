import type { OnboardingPhase } from '@/shared/preferences/preferences'
import { onboardingPhases } from '@/shared/preferences/preferences'

export type { OnboardingPhase }

// The account's phase lives on the server (PlayerPreferences.onboarding_phase).
// This cache only mirrors it so a reload resumes the journey at the right step
// without waiting on the request; an account we have never seen here resolves
// to "done", which is what keeps existing players out of the tour.
const sessionPhases = new Map<number, OnboardingPhase>()
export const onboardingStorageKey = (userId: number) => `git-it-app-onboarding:v3:${userId}`

export function readCachedOnboardingPhase(userId: number): OnboardingPhase | null {
  try {
    const value = window.localStorage.getItem(onboardingStorageKey(userId))
    if (onboardingPhases.includes(value as OnboardingPhase)) return value as OnboardingPhase
  } catch {
    // Privacy modes may block storage; the server phase still drives the journey.
  }
  return sessionPhases.get(userId) ?? null
}

export function writeOnboardingPhase(userId: number, phase: OnboardingPhase) {
  sessionPhases.set(userId, phase)
  try {
    window.localStorage.setItem(onboardingStorageKey(userId), phase)
  } catch {
    // Navigation can still continue with the in-memory state.
  }
}
