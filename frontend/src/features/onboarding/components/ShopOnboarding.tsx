import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { storyPath } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'

export function ShopOnboarding({ ready, hasCompanion, ownsCompanion, canBuy }: {
  ready: boolean
  hasCompanion: boolean
  ownsCompanion: boolean
  canBuy: boolean
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  if (!onboarding || !['shop', 'purchase'].includes(onboarding.phase)) return null

  function returnToMap() {
    onboarding!.setPhase('done')
    navigate(storyPath())
  }

  let title = 'Choose a companion to play'
  let message = 'Pick a portrait, then select Purchase. Your first companion equips automatically. You need one to enter any level.'
  let action: ReactNode = null

  if (hasCompanion) {
    title = 'Companion ready — start playing'
    message = 'Your companion is equipped. Head back to the map and open your first level.'
    action = <Button size="sm" data-onboarding="shop-back-to-map" onClick={returnToMap}>Back to map</Button>
  } else if (ownsCompanion) {
    title = 'Equip your companion'
    message = 'You already own a companion. Go to Home → Profile and equip it before entering a level.'
    action = <Button size="sm" data-onboarding="shop-back-to-map" onClick={returnToMap}>Back to map</Button>
  } else if (ready && !canBuy) {
    title = 'Companion required'
    message = 'Purchases are unavailable right now. Return to the map and come back later to choose a companion.'
    action = <Button size="sm" variant="outline" data-onboarding="shop-back-to-map" onClick={returnToMap}>Back to map</Button>
  }

  return (
    <OnboardingBanner
      title={title}
      actions={action}
    >
      {message}
    </OnboardingBanner>
  )
}
