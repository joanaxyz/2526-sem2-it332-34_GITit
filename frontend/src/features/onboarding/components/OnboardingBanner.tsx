import type { ReactNode } from 'react'
import { Route } from 'lucide-react'

export function OnboardingBanner({ title, children, actions, onSkip, skipLabel = 'Explore on my own' }: {
  title: string
  children: ReactNode
  actions?: ReactNode
  onSkip?: () => void
  skipLabel?: string
}) {
  return (
    <aside className="app-onboarding-banner" aria-label="Getting started" data-onboarding="setup-progress">
      <Route aria-hidden="true" />
      <div className="app-onboarding-banner__copy">
        <strong>{title}</strong>
        <p>{children}</p>
      </div>
      <div className="app-onboarding-banner__actions">
        {actions}
        {onSkip ? (
          <button type="button" className="app-onboarding-skip" onClick={onSkip}>{skipLabel}</button>
        ) : null}
      </div>
    </aside>
  )
}
