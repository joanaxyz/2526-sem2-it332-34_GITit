import type { ReactNode } from 'react'
import { Route } from 'lucide-react'

import { useAppOnboarding } from './onboardingContext'

export function OnboardingBanner({ step, children, actions }: { step: number; children: ReactNode; actions?: ReactNode }) {
  const onboarding = useAppOnboarding()
  return (
    <aside className="app-onboarding-banner" aria-label="Getting started" data-onboarding="setup-progress">
      <Route aria-hidden="true" />
      <div className="app-onboarding-banner__copy">
        <strong>Getting started · {step} of 3</strong>
        <p>{children}</p>
      </div>
      <div className="app-onboarding-banner__actions">
        {actions}
        <button type="button" className="app-onboarding-skip" onClick={() => onboarding?.setPhase('done')}>Skip setup</button>
      </div>
    </aside>
  )
}
