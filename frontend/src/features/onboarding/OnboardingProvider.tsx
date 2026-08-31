import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'

import { queryKeys } from '@/shared/api/queryKeys'
import { HOME_ROUTE, SHOP_ROUTE } from '@/shared/navigation/routes'
import { preferencesApi } from '@/shared/preferences/preferencesApi'
import type { PlayerAccountPreferences } from '@/shared/preferences/preferences'

import { OnboardingContext } from './onboardingContext'
import { readCachedOnboardingPhase, writeOnboardingPhase, type OnboardingPhase } from './onboardingState'

// HomeLayout keys this provider by account, while keeping it mounted across pages.
export function OnboardingProvider({ userId, children }: { userId?: number; children: ReactNode }) {
  const { pathname } = useLocation()
  const queryClient = useQueryClient()
  // Registration is what starts the journey, server-side. Anyone else - an
  // existing player, a fresh browser, a second device - resolves to "done".
  const [localPhase, setLocalPhase] = useState<OnboardingPhase | null>(
    () => userId == null ? null : readCachedOnboardingPhase(userId),
  )
  const preferences = useQuery({
    queryKey: queryKeys.preferences,
    queryFn: preferencesApi.get,
    enabled: userId != null,
    staleTime: 10 * 60 * 1000,
    retry: false,
  })
  const { mutate: savePhase } = useMutation({
    mutationFn: (phase: OnboardingPhase) => preferencesApi.update({ onboarding_phase: phase }),
    onSuccess: (data) => queryClient.setQueryData(queryKeys.preferences, data),
  })
  const phase: OnboardingPhase = localPhase ?? preferences.data?.onboarding_phase ?? 'done'

  const setPhase = useCallback((next: OnboardingPhase) => {
    setLocalPhase(next)
    if (userId == null) return
    writeOnboardingPhase(userId, next)
    queryClient.setQueryData<PlayerAccountPreferences>(queryKeys.preferences, (current) => (
      current ? { ...current, onboarding_phase: next } : current
    ))
    // A failed write only costs the player a repeated step next session; the
    // journey itself must never block on the round trip.
    savePhase(next)
  }, [queryClient, savePhase, userId])

  useEffect(() => {
    // Cache what the server says so the next load resumes without a flash.
    const served = preferences.data?.onboarding_phase
    if (userId == null || served == null || localPhase != null) return
    setLocalPhase(served)
    writeOnboardingPhase(userId, served)
  }, [localPhase, preferences.data?.onboarding_phase, userId])

  useEffect(() => {
    // Follow users who use the normal navigation instead of a tutorial CTA.
    if (phase === 'stories' && pathname === SHOP_ROUTE) setPhase('shop')
    if (['stories', 'shop', 'purchase'].includes(phase) && pathname === HOME_ROUTE) setPhase('home')
  }, [pathname, phase, setPhase])
  const value = useMemo(() => ({ phase, setPhase }), [phase, setPhase])
  return <OnboardingContext.Provider value={value}>{children}</OnboardingContext.Provider>
}
