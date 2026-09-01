import { Backpack, BookOpen, CalendarDays, Coins, Compass, Gauge, Route, Swords, Target, Trophy, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { SHOP_ROUTE, storyPath } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'
import { useAppOnboarding } from './onboardingContext'

export type HomeTourSection = 'overview' | 'loadout' | 'profile'

// The hub tour walks one section per Home tab. Only the first step of a section
// is required; the rest depend on what the account already owns.
const sectionOrder = ['loadout', 'overview', 'profile'] as const

const loadoutSteps = [
  {
    id: 'hub', selector: '[data-onboarding="home-loadout"]', icon: Backpack,
    title: 'Home is your character hub',
    body: 'Home has three sections. Loadout holds the companions you own, Overview tracks your progress, and Profile shows your rank and skills. We will walk through each one.',
  },
  {
    id: 'roster', selector: '[data-onboarding="loadout-roster"]', icon: UserRound,
    title: 'Your owned roster',
    body: 'Every companion you buy lands here. Select one to inspect it; the stage above shows the companion you are currently looking at.',
    optional: true,
  },
  {
    id: 'equipped', selector: '[data-onboarding="home-equip"]', icon: Swords,
    title: 'Equip who joins you',
    body: 'Equip companion sends the selected companion into your next Adventure or Challenge. Your first purchase is already equipped, so this only matters when you want to switch.',
    optional: true,
  },
  {
    id: 'worlds', selector: '[data-onboarding="loadout-worlds"]', icon: Compass,
    title: 'Worlds you can enter',
    body: 'The story worlds you own are listed below. Open story map takes you straight to that world and its chapters.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const overviewSteps = [
  {
    id: 'next', selector: '[data-onboarding="overview-next"]', icon: Route,
    title: 'Overview opens on your next step',
    body: 'The top card always points at the most useful thing to do next: choose your first companion, or continue the story from the next available level.',
  },
  {
    id: 'mastery', selector: '[data-onboarding="overview-mastery"]', icon: Gauge,
    title: 'Git Skill Mastery',
    body: 'Each bar is one family of Git commands and how reliably you use it. The orb on the right averages them into your overall mastery and proficiency stars.',
    optional: true,
  },
  {
    id: 'activity', selector: '[data-onboarding="overview-progress"]', icon: CalendarDays,
    title: 'Activity and story progress',
    body: 'The heatmap shows your last 14 days of practice; short regular sessions beat one long one. Story Progress counts levels cleared, perfect clears, and hard trials won.',
    optional: true,
  },
  {
    id: 'kpis', selector: '[data-onboarding="overview-kpis"]', icon: Target,
    title: 'Where your runs stand',
    body: 'Clear rate, hard clear rate, average retries per cleared run, and command accuracy. Accuracy stays hidden until you have run 100 commands.',
    optional: true,
  },
  {
    id: 'achievements', selector: '[data-onboarding="overview-achievements"]', icon: Trophy,
    title: 'Achievements to chase',
    body: 'Every achievement shows its progress and point value. Filter by Unlocked or Locked to see what is still open to you.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const profileSteps = [
  {
    id: 'switch', selector: '[data-onboarding="profile-switch"]', icon: UserRound,
    title: 'Profile and Rank Ladder',
    body: 'Profile shows who you are playing as. Rank Ladder lists every tier, from the ones you cleared to the ones still locked.',
  },
  {
    id: 'rank', selector: '[data-onboarding="profile-rank"]', icon: Trophy,
    title: 'Your rank and XP',
    body: 'The badge is your current rank, and the meter under it tracks XP toward the next tier. Clearing Adventure levels and Challenge trials is what moves it.',
    optional: true,
  },
  {
    id: 'currencies', selector: '[data-onboarding="profile-currencies"]', icon: Coins,
    title: 'GitCoins and perfect clears',
    body: 'GitCoins are what you spend on companions in the Shop. Perfect clears count the levels you finished flawlessly.',
    optional: true,
  },
  {
    id: 'spellbook', selector: '[data-onboarding="profile-spellbook"]', icon: BookOpen,
    title: 'Spells you have learned',
    body: 'Every Git command you solve a level with is inscribed here. Select a spell to watch your companion cast it on the sprite stage.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const sections = {
  loadout: { label: 'Home tour · Loadout', steps: loadoutSteps },
  overview: { label: 'Home tour · Overview', steps: overviewSteps },
  profile: { label: 'Home tour · Profile', steps: profileSteps },
} satisfies Record<HomeTourSection, { label: string; steps: readonly WorkspaceTourStep[] }>

export function HomeOnboarding({ ready, hasCompanion, tab, onSelectTab }: {
  ready: boolean
  hasCompanion: boolean
  tab: HomeTourSection
  onSelectTab: (tab: HomeTourSection) => void
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  const [started, setStarted] = useState(false)
  const phase = onboarding?.phase

  useEffect(() => {
    // The tour always enters at Loadout, even for players who reached Home
    // through the normal navigation instead of the Shop CTA.
    if (phase !== 'home' || !ready || started) return
    if (tab !== 'loadout') onSelectTab('loadout')
    else setStarted(true)
  }, [onSelectTab, phase, ready, started, tab])

  if (!onboarding || !['home', 'equip'].includes(onboarding.phase)) return null
  const loadoutTab = tab === 'loadout'

  function finish() {
    onboarding!.setPhase('done')
    navigate(storyPath())
  }

  function advance() {
    const next = sectionOrder[sectionOrder.indexOf(tab) + 1]
    if (next) onSelectTab(next)
    else if (hasCompanion) finish()
    else {
      onboarding!.setPhase('equip')
      onSelectTab('loadout')
    }
  }

  return (
    <>
      <OnboardingBanner step={3} actions={
        hasCompanion
          ? <Button size="sm" onClick={finish}>Return to Stories</Button>
          : <Button size="sm" variant="outline" onClick={() => {
            if (loadoutTab) { onboarding.setPhase('purchase'); navigate(`${SHOP_ROUTE}?tab=companions`) }
            else onSelectTab('loadout')
          }}>{loadoutTab ? 'Back to Shop' : 'Open Loadout'}</Button>
      }>
        {hasCompanion
          ? 'Your companion is equipped. Explore Loadout, Overview, and Profile, then return to Stories to play.'
          : 'In Loadout, select a character you own and press Equip companion. If your roster is empty, buy a character in the Shop first.'}
      </OnboardingBanner>
      {ready && started && onboarding.phase === 'home' ? (
        <GameplayWorkspaceTour
          key={tab}
          label={sections[tab].label}
          finishLabel={tab === 'loadout'
            ? 'Show Overview'
            : tab === 'overview'
              ? 'Show Profile'
              : hasCompanion ? 'Return to Stories' : 'Check my loadout'}
          steps={sections[tab].steps}
          onClose={(reason) => {
            if (reason === 'skip') onboarding.setPhase('done')
            else advance()
          }}
        />
      ) : null}
    </>
  )
}
