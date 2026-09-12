import { createContext, useContext } from 'react'
import type { OnboardingPhase } from '@/features/onboarding/utils/onboardingState'

export const OnboardingContext = createContext<{
  phase: OnboardingPhase
  setPhase: (phase: OnboardingPhase) => void
} | null>(null)

export const useAppOnboarding = () => useContext(OnboardingContext)
