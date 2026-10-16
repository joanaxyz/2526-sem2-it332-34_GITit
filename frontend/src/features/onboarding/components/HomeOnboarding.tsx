import { BookOpen, CalendarDays, LayoutList, Swords, Trophy, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { storyPath } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'

export type HomeTourSection = 'overview' | 'profile'

function sectionFor(view: HomeView): HomeTourSection {
  return view === 'profile' ? 'profile' : 'overview'
}

const overviewSteps = [
  {
    id: 'views',
    selector: '[data-onboarding="home-views"]',
    icon: LayoutList,
    title: 'Switch Home views here',
    body: 'Use this menu to open Profile, Progress, or Skills & achievements.',
  },
  {
    id: 'progress',
    selector: '[data-onboarding="overview-progress"]',
    icon: CalendarDays,
    title: 'Track your progress',
    body: 'See your recent practice, completion rate, and run history here.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const profileSteps = [
  {
    id: 'ladder',
    selector: '[data-onboarding="profile-ladder"]',
    icon: UserRound,
    title: 'See the rank ladder',
    body: 'Your current tier is highlighted. Locked tiers show what comes next.',
  },
  {
    id: 'rank',
    selector: '[data-onboarding="profile-rank"]',
    icon: Trophy,
    title: 'Follow your rank progress',
    body: 'Completing Adventures and Challenges moves this meter toward your next rank.',
    optional: true,
  },
  {
    id: 'roster',
    selector: '[data-onboarding="profile-roster"]',
    icon: Swords,
    title: 'Manage your companions',
    body: 'Choose an owned companion and select Equip companion before entering a level.',
    optional: true,
  },
  {
    id: 'spellbook',
    selector: '[data-onboarding="profile-spellbook"]',
    icon: BookOpen,
    title: 'Review learned commands',
    body: 'Commands you use successfully appear here as spells.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const sections = {
  overview: { label: 'Home tour · Progress', steps: overviewSteps },
  profile: { label: 'Home tour · Profile', steps: profileSteps },
} satisfies Record<HomeTourSection, { label: string; steps: readonly WorkspaceTourStep[] }>

export function HomeOnboarding({ ready, hasCompanion, view, onSelectView }: {
  ready: boolean
  hasCompanion: boolean
  view: HomeView
  onSelectView: (view: HomeView) => void
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  const [started, setStarted] = useState(false)
  const phase = onboarding?.phase
  const section = sectionFor(view)

  useEffect(() => {
    if (phase !== 'home' || !ready || started) return
    if (view === 'profile') onSelectView('progress')
    else setStarted(true)
  }, [onSelectView, phase, ready, started, view])

  if (!onboarding || !['home', 'equip'].includes(onboarding.phase)) return null
  const profileView = view === 'profile'

  function finish() {
    if (!hasCompanion) return
    onboarding!.setPhase('done')
    navigate(storyPath())
  }

  function continueCompanionSetup() {
    onboarding!.setPhase('equip')
    onSelectView('profile')
  }

  function advance() {
    if (section === 'overview') onSelectView('profile')
    else if (hasCompanion) finish()
    else continueCompanionSetup()
  }

  return (
    <>
      <OnboardingBanner
        title="Step 3 of 3 · Explore Home"
        actions={hasCompanion
          ? <Button size="sm" onClick={finish}>Return to map</Button>
          : profileView
            ? null
            : <Button size="sm" variant="outline" onClick={() => onSelectView('profile')}>Open Profile</Button>}
        onSkip={onboarding.phase === 'home'
          ? (hasCompanion ? finish : continueCompanionSetup)
          : undefined}
        skipLabel="Skip Home tour"
      >
        {hasCompanion
          ? 'Your companion is equipped. Review Home, then return to the map.'
          : profileView
            ? 'Equip a companion you own. If your roster is empty, choose one in the Shop.'
            : 'Review your progress, then open Profile to set up the companion required for levels.'}
      </OnboardingBanner>

      {ready && started && onboarding.phase === 'home' ? (
        <GameplayWorkspaceTour
          key={section}
          label={sections[section].label}
          finishLabel={section === 'overview'
            ? 'Show Profile'
            : hasCompanion ? 'Return to map' : 'Set up companion'}
          steps={sections[section].steps}
          onClose={(reason) => {
            if (reason === 'skip') {
              if (hasCompanion) finish()
              else continueCompanionSetup()
            } else advance()
          }}
        />
      ) : null}
    </>
  )
}
