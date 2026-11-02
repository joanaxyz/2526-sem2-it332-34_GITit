import { useCallback, useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { startBackgroundMusic, stopBackgroundMusic } from '@/shared/audio/battleAudio'
import { AnchoredCoachmark } from '@/shared/components/AnchoredCoachmark'
import { CursorGlow } from '@/shared/components/CursorGlow'
import { OnboardingProvider } from '@/features/onboarding/components/OnboardingProvider'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { useAuthStore } from '@/shared/auth/useAuth'
import { AppMobileNav, AppTopbar } from '@/shared/navigation/AppNavigation'
import { HOME_ROUTE, SHOP_ROUTE, isStoryMapRoute } from '@/shared/navigation/routes'
import { HomeTutor } from '@/shared/tutoring/HomeTutor'
import { cn } from '@/shared/utils/cn'
import {
  hasSeenWorldMascotCoachmark,
  hasSeenAskBlueCoachmark,
  markAskBlueCoachmarkSeen,
} from '@/shared/level/utils/milestones'

// Phases where the tutor window should not auto-open so onboarding UI has space.
const TUTOR_SUPPRESS_PHASES = new Set(['welcome', 'orientation', 'stories'])

function HomeTutorWithOnboarding({ tutorKey, userId }: { tutorKey: string; userId?: number }) {
  const onboarding = useAppOnboarding()
  const suppressOpen = onboarding != null && TUTOR_SUPPRESS_PHASES.has(onboarding.phase)
  const isStoryMap = isStoryMapRoute(useLocation().pathname)

  // Track mascot-seen reactively so Ask Blue fires in the same session the
  // user dismisses the mascot coachmark, not just on a future page load.
  const [mascotSeen, setMascotSeen] = useState(() => hasSeenWorldMascotCoachmark(userId))
  useEffect(() => {
    setMascotSeen(hasSeenWorldMascotCoachmark(userId))
  }, [userId])
  useEffect(() => {
    const onSeen = () => setMascotSeen(true)
    window.addEventListener('milestone:world-mascot-coachmark-seen', onSeen)
    return () => window.removeEventListener('milestone:world-mascot-coachmark-seen', onSeen)
  }, [])

  const [askBlueCoachmarkVisible, setAskBlueCoachmarkVisible] = useState(false)

  useEffect(() => {
    if (!isStoryMap) return
    if (suppressOpen) return
    if (!mascotSeen) return
    if (hasSeenAskBlueCoachmark(userId)) return
    const timer = setTimeout(() => setAskBlueCoachmarkVisible(true), 1200)
    return () => clearTimeout(timer)
  }, [isStoryMap, suppressOpen, mascotSeen, userId])

  const dismissAskBlueCoachmark = useCallback(() => {
    markAskBlueCoachmarkSeen(userId)
    setAskBlueCoachmarkVisible(false)
  }, [userId])

  return (
    <>
      <HomeTutor key={tutorKey} suppressOpen={suppressOpen} />
      {askBlueCoachmarkVisible ? (
        <AnchoredCoachmark
          targetSelector='[data-mascot-launcher="home-tutor"]'
          title="Need help? Ask Blue!"
          body="Ask Blue questions about Git, commands, or anything you're unsure about. You can open it anytime!"
          onDismiss={dismissAskBlueCoachmark}
        />
      ) : null}
    </>
  )
}

export function HomeLayout() {
  const userId = useAuthStore((state) => state.user?.id)
  const location = useLocation()
  const isStoryMapPage = isStoryMapRoute(location.pathname)
  const showTutor = isStoryMapPage || location.pathname === HOME_ROUTE || location.pathname === SHOP_ROUTE

  useEffect(() => {
    startBackgroundMusic('outside')
    return () => stopBackgroundMusic('outside')
  }, [])

  return (
    <div className="app-shell">
      <a className="skip-link" href="#app-main-content">Skip to content</a>
      <CursorGlow />
      <AppTopbar />
      <main id="app-main-content" tabIndex={-1} className={cn('app-main', isStoryMapPage && 'app-main--story-map')}>
        <OnboardingProvider key={userId ?? 'guest'} userId={userId}>
          <Outlet />
          {showTutor ? <HomeTutorWithOnboarding tutorKey={String(userId ?? 'guest')} userId={userId} /> : null}
        </OnboardingProvider>
      </main>
      <AppMobileNav />
    </div>
  )
}
