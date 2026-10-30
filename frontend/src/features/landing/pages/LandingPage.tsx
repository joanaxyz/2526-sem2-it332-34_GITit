import { Navigate } from 'react-router-dom'

import { LandingHeader, LandingHero } from '@/features/landing/components/LandingHero'
import { ClosingCall, EncounterBand, HowItWorks, SpireClimb } from '@/features/landing/components/LandingSections'
import { useAuthStore } from '@/shared/auth/useAuth'
import { storyPath } from '@/shared/navigation/routes'

export function LandingPage() {
  // A session already live in this tab goes straight to the story map. A cold
  // tab shows the landing page; its sign-in links aim at the story map so
  // Protected can restore a saved session before falling back to /login.
  const signedIn = useAuthStore((state) => Boolean(state.accessToken && state.user))
  if (signedIn) return <Navigate replace to={storyPath()} />

  return (
    <div className="landing">
      <LandingHeader />
      <main>
        <LandingHero />
        <HowItWorks />
        <SpireClimb />
        <EncounterBand />
        <ClosingCall />
      </main>
      <footer className="landing-footer">
        <span>GIT it!</span>
        <span>Scenario-driven Git practice</span>
      </footer>
    </div>
  )
}
