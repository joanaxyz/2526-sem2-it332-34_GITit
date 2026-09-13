import { BookOpen, CalendarDays, LayoutList, Swords, Trophy, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { SHOP_ROUTE, storyPath } from '@/shared/navigation/routes'
import { OnboardingBanner } from './OnboardingBanner'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'

export type HomeTourSection = 'overview' | 'profile'

// The hub tour walks two sections in order: the data categories a learner reads,
// then the Profile category where they equip a companion. Only the first step of
// a section is required; the rest depend on what the account already owns.

/** Profile is its own tour section; every other category shares the first one. */
function sectionFor(view: HomeView): HomeTourSection {
  return view === 'profile' ? 'profile' : 'overview'
}

const overviewSteps = [
  {
    id: 'views', selector: '[data-onboarding="home-views"]', icon: LayoutList,
    title: 'Home is one dropdown',
    body: 'Home has three views: Profile, Progress, and Skills & achievements. Switch between them here; the line beside the dropdown says what each one covers.',
  },
  {
    id: 'progress', selector: '[data-onboarding="overview-progress"]', icon: CalendarDays,
    title: 'Your progress',
    body: 'The plot shows how much you practised — pick Week, Month or Year to change the span. The citadel beside it fills with the share of runs you finished, and your full record sits underneath.',
    optional: true,
  },
] satisfies WorkspaceTourStep[]

const profileSteps = [
  {
    id: 'ladder', selector: '[data-onboarding="profile-ladder"]', icon: UserRound,
    title: 'The rank ladder',
    body: 'Every tier is listed here, from the ones you cleared to the ones still locked. Your current tier is the highlighted row.',
  },
  {
    id: 'rank', selector: '[data-onboarding="profile-rank"]', icon: Trophy,
    title: 'Your rank progress',
    body: 'The badge is your current rank, and the meter under it tracks mastery toward the next tier. Clearing Adventure levels and Challenge trials is what moves it.',
    optional: true,
  },
  {
    id: 'roster', selector: '[data-onboarding="profile-roster"]', icon: Swords,
    title: 'Your companion',
    body: 'Every companion you own is listed here. Select one and press Equip companion to send it into your next Adventure or Challenge; your first purchase is already equipped.',
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
  overview: { label: 'Home tour · Views', steps: overviewSteps },
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
    // The tour always enters on the data categories, even for players who reached
    // Home through normal navigation instead of the Shop CTA.
    if (phase !== 'home' || !ready || started) return
    if (view === 'profile') onSelectView('progress')
    else setStarted(true)
  }, [onSelectView, phase, ready, started, view])

  if (!onboarding || !['home', 'equip'].includes(onboarding.phase)) return null
  const profileView = view === 'profile'

  function finish() {
    onboarding!.setPhase('done')
    navigate(storyPath())
  }

  function advance() {
    if (section === 'overview') onSelectView('profile')
    else if (hasCompanion) finish()
    else {
      onboarding!.setPhase('equip')
      onSelectView('profile')
    }
  }

  return (
    <>
      <OnboardingBanner step={3} actions={
        hasCompanion
          ? <Button size="sm" onClick={finish}>Return to Stories</Button>
          : <Button size="sm" variant="outline" onClick={() => {
            if (profileView) { onboarding.setPhase('purchase'); navigate(SHOP_ROUTE) }
            else onSelectView('profile')
          }}>{profileView ? 'Back to Shop' : 'Open Profile'}</Button>
      }>
        {hasCompanion
          ? 'Your companion is equipped. Look through each Home view, then return to Stories to play.'
          : 'In Profile, select a character you own and press Equip companion. If your roster is empty, buy a character in the Shop first.'}
      </OnboardingBanner>
      {ready && started && onboarding.phase === 'home' ? (
        <GameplayWorkspaceTour
          key={section}
          label={sections[section].label}
          finishLabel={section === 'overview'
            ? 'Show Profile'
            : hasCompanion ? 'Return to Stories' : 'Equip a companion'}
          steps={sections[section].steps}
          onClose={(reason) => {
            if (reason === 'skip') onboarding.setPhase('done')
            else advance()
          }}
        />
      ) : null}
    </>
  )
}
