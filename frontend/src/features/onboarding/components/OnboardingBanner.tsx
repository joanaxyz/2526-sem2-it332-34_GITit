import type { ReactNode } from 'react'
import { Route } from 'lucide-react'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'

export function OnboardingBanner({ step, children, actions, onSkip }: {
  step: number
  children: ReactNode
  actions?: ReactNode
  /** Replaces ending the whole journey, for steps that only skip themselves. */
  onSkip?: () => void
}) {
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
        <button type="button" className="app-onboarding-skip" onClick={onSkip ?? (() => onboarding?.setPhase('done'))}>Skip setup</button>
      </div>
    </aside>
  )
}
