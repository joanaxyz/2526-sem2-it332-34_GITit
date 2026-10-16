import { Coins, ShoppingBag, UserRound } from 'lucide-react'
import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { HOME_ROUTE } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'

const shopSteps = [
  {
    id: 'wallet',
    selector: '[data-onboarding="wallet-balance"]',
    icon: Coins,
    title: 'Check your GitCoins',
    body: 'Your balance is shown here. A purchase only spends the price shown in the Shop.',
  },
  {
    id: 'character',
    selector: '[data-onboarding="shop-characters"]',
    icon: UserRound,
    title: 'Preview a companion',
    body: 'Choose a portrait to see that companion’s poses and skills.',
  },
  {
    id: 'purchase',
    selector: '[data-onboarding="shop-purchase"]',
    icon: ShoppingBag,
    title: 'Purchase your companion',
    body: 'Select Purchase when you are ready. Your first companion equips automatically.',
  },
] satisfies WorkspaceTourStep[]

export function ShopOnboarding({ ready, hasCompanion, ownsCompanion, canBuy }: {
  ready: boolean
  hasCompanion: boolean
  ownsCompanion: boolean
  canBuy: boolean
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  if (!onboarding || !['shop', 'purchase'].includes(onboarding.phase)) return null

  function skipShopTour() {
    onboarding!.setPhase('purchase')
  }

  function visitHome() {
    onboarding!.setPhase('home')
    navigate(HOME_ROUTE)
  }

  let title = 'Step 2 of 3 · Choose a companion'
  let message = 'Pick a portrait, then select Purchase. Your first companion equips automatically.'
  let action: ReactNode = null

  if (hasCompanion) {
    title = 'Step 2 of 3 · Companion ready'
    message = 'Your companion is equipped. Visit Home to see your profile and progress.'
    action = <Button size="sm" onClick={visitHome}>Explore Home</Button>
  } else if (ownsCompanion) {
    title = 'Step 2 of 3 · Equip your companion'
    message = 'You already own a companion. Visit Home and equip it in Profile before you play.'
    action = <Button size="sm" onClick={visitHome}>Open Home</Button>
  } else if (ready && !canBuy) {
    title = 'Step 2 of 3 · Companion required'
    message = 'You need an equipped companion to play. Purchases are unavailable right now, so you can review Home and return here later.'
    action = <Button size="sm" variant="outline" onClick={visitHome}>Explore Home</Button>
  }

  return (
    <>
      <OnboardingBanner
        title={title}
        actions={action}
        onSkip={onboarding.phase === 'shop' && !ownsCompanion ? skipShopTour : undefined}
        skipLabel="Skip shop tour"
      >
        {message}
      </OnboardingBanner>
      {ready && !ownsCompanion && onboarding.phase === 'shop' ? (
        <GameplayWorkspaceTour
          label="Shop tour"
          finishLabel="Choose a companion"
          steps={shopSteps}
          onClose={skipShopTour}
        />
      ) : null}
    </>
  )
}
