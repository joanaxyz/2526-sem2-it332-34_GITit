import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'

import { queryKeys } from '@/shared/api/queryKeys'
import { HOME_ROUTE, SHOP_ROUTE } from '@/shared/navigation/routes'
import { preferencesApi } from '@/shared/preferences/preferencesApi'
import type { PlayerAccountPreferences } from '@/shared/preferences/preferences'

import { OnboardingContext } from '@/features/onboarding/hooks/onboardingContext'
import {
  readCachedOnboardingPhase,
  writeOnboardingPhase,
  type OnboardingPhase,
} from '@/features/onboarding/utils/onboardingState'

// HomeLayout keys this provider by account, while keeping it mounted across pages.
export function OnboardingProvider({ userId, children }: { userId?: number; children: ReactNode }) {
  const { pathname } = useLocation()
  const queryClient = useQueryClient()
  const changedInThisSession = useRef(false)
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
    scope: { id: `onboarding:${userId ?? 'guest'}` },
    onSuccess: (data) => queryClient.setQueryData(queryKeys.preferences, data),
  })
  const preferencesSettled = userId == null || preferences.isSuccess || preferences.isError
  // A browser cache is useful as an offline fallback, but it is not safe to
  // expose as an actionable phase while the account preference is pending.
  // Otherwise a child can advance stale state and overwrite a newer server
  // value before the initial read finishes.
  const phase: OnboardingPhase = changedInThisSession.current
    ? localPhase ?? preferences.data?.onboarding_phase ?? 'done'
    : preferences.data?.onboarding_phase ?? (preferencesSettled ? localPhase ?? 'done' : 'done')
  const routePhase = changedInThisSession.current
    ? phase
    : preferences.data?.onboarding_phase ?? phase

  const setPhase = useCallback((next: OnboardingPhase) => {
    changedInThisSession.current = true
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
    // The server is authoritative across devices. Replace cached phases unless
    // this mount already advanced the journey and has an in-flight write.
    const served = preferences.data?.onboarding_phase
    if (userId == null || served == null || changedInThisSession.current) return
    setLocalPhase(served)
    writeOnboardingPhase(userId, served)
  }, [preferences.data?.onboarding_phase, userId])

  useEffect(() => {
    // Follow users who use the normal navigation instead of a tutorial CTA.
    // Never derive a write from the browser cache while the authoritative
    // account preference is still loading: an old "welcome" value must not
    // resurrect onboarding for an account the server already marked done.
    if (!preferencesSettled) return
    if (pathname === SHOP_ROUTE) {
      if (['welcome', 'orientation', 'stories'].includes(routePhase)) setPhase('shop')
      else if (['home', 'equip'].includes(routePhase)) setPhase('purchase')
    }
    if (
      pathname === HOME_ROUTE
      && ['welcome', 'orientation', 'stories', 'shop', 'purchase'].includes(routePhase)
    ) setPhase('home')
  }, [pathname, preferencesSettled, routePhase, setPhase])
  const value = useMemo(() => ({ phase, setPhase }), [phase, setPhase])
  return <OnboardingContext.Provider value={value}>{children}</OnboardingContext.Provider>
}
