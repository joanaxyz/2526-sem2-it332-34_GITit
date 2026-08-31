import { Coins, ShoppingBag, UserRound } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { HOME_ROUTE } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'
import { useAppOnboarding } from './onboardingContext'

const shopSteps = [
  {
    id: 'wallet', selector: '[data-onboarding="shop-balance"]', icon: Coins,
    title: 'Check your GitCoins',
    body: 'Characters are called companions here. Each one has a GitCoin price. Check your balance before choosing; the tutorial never spends coins for you.',
  },
  {
    id: 'character', selector: '[data-onboarding="shop-characters"]', icon: UserRound,
    title: 'Choose your character',
    body: 'Select a portrait to preview that companion. You can browse the character’s poses and skills before deciding which one to buy.',
    optional: true,
  },
  {
    id: 'purchase', selector: '[data-onboarding="shop-purchase"]', icon: ShoppingBag,
    title: 'Buy the selected companion',
    body: 'When you are ready, use the purchase button with the GitCoin price. Your first companion equips automatically. After the purchase succeeds, choose Visit Home above to see your loadout.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

export function ShopOnboarding({ ready, companionsTab, ownsCompanion, canBuy }: {
  ready: boolean
  companionsTab: boolean
  ownsCompanion: boolean
  canBuy: boolean
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  if (!onboarding || !['shop', 'purchase'].includes(onboarding.phase)) return null

  function visitHome() {
    onboarding!.setPhase('home')
    navigate(`${HOME_ROUTE}?tab=loadout`)
  }

  return (
    <>
      <OnboardingBanner step={2} actions={
        ownsCompanion ? <Button size="sm" onClick={visitHome}>Visit Home</Button> :
          ready && !canBuy ? <Button size="sm" variant="outline" onClick={visitHome}>Continue without buying</Button> : null
      }>
        {ownsCompanion
          ? 'Your character is owned. Next, visit Home to check your equipped companion and explore your progress.'
          : !companionsTab
            ? 'Open the Companions tab to choose and buy your character.'
            : ready && !canBuy
              ? 'No companion can be purchased with your current balance right now. You can still explore Home or skip setup and return later.'
              : 'Choose a portrait, check its price, and press the purchase button. Once it succeeds, we will continue to Home.'}
      </OnboardingBanner>
      {ready && companionsTab && !ownsCompanion && onboarding.phase === 'shop' ? (
        <GameplayWorkspaceTour label="Shop welcome tour" finishLabel="Choose my character" steps={shopSteps}
          onClose={(reason) => onboarding.setPhase(reason === 'skip' ? 'done' : 'purchase')} />
      ) : null}
    </>
  )
}
