import { BookOpen, CircleHelp, GitBranch, Play, Sparkles, Swords } from 'lucide-react'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { HOME_ROUTE, SHOP_ROUTE } from '@/shared/navigation/routes'

export function StoryOnboarding({ ready, compact, hasCompanion }: {
  ready: boolean
  compact: boolean
  hasCompanion: boolean
}) {
  const onboarding = useAppOnboarding()
  const navigate = useNavigate()
  const steps = useMemo(() => [
    {
      id: 'welcome',
      selector: '[data-onboarding="stories"]',
      icon: GitBranch,
      title: 'Your Git journey starts here',
      body: 'Stories is your starting point for learning Git safely. We’ll explore the map, visit the Shop to buy your character, then stop at Home before your first level. Your real projects stay untouched.',
    },
    {
      id: 'learn',
      selector: compact ? '[aria-controls="story-map-tools"]' : '.chapter-book',
      icon: BookOpen,
      title: 'Read before you practice',
      body: compact
        ? 'Open Chapter tools to find the Chapter Book. Its Field Guide explains this chapter’s commands and examples before you enter a level.'
        : 'The Chapter Book opens this chapter’s Field Guide. Read the commands and examples here before entering a level.',
    },
    {
      id: 'challenges',
      selector: '[data-onboarding="challenges"]',
      icon: Swords,
      title: 'Practice, then test your skills',
      body: 'Clear every Adventure level in the chapter to unlock its Challenge Gate. Then work through Easy, Medium, and Hard trials. The workspace tours explain commands, scoring, and completion when you play.',
      optional: true,
    },
    {
      id: 'play',
      selector: '[data-onboarding="next-level"]',
      icon: Play,
      title: 'Open your next level',
      body: 'When your character is ready, select this numbered level and press the Play button that appears. Read its objective and use Git commands to solve it.',
      optional: true,
    },
    {
      id: 'companion',
      selector: compact ? '[aria-controls="story-map-utilities"]' : '.story-companion-panel',
      icon: Sparkles,
      title: hasCompanion ? 'Visit the Shop, then Home' : 'Let’s choose your character',
      body: (compact ? 'Story utilities holds your chapters and companion. ' : '') + (hasCompanion
        ? 'You already have a companion, so there’s no need to buy another. Let’s visit the Shop, then Home to see your character and progress.'
        : 'Adventures need an equipped companion. Next we’ll go to the Shop, choose a character, and buy it with GitCoins. Then we’ll check your loadout in Home.'),
    },
  ] satisfies WorkspaceTourStep[], [compact, hasCompanion])

  if (!onboarding) return null
  const resuming = !['stories', 'done'].includes(onboarding.phase)

  return (
    <>
      <Button type="button" variant="ghost" size="sm" disabled={!ready} onClick={() => {
        if (resuming) navigate(['shop', 'purchase'].includes(onboarding.phase) ? `${SHOP_ROUTE}?tab=companions` : `${HOME_ROUTE}?tab=loadout`)
        else onboarding.setPhase('stories')
      }}>
        <CircleHelp aria-hidden="true" />
        {resuming ? 'Continue setup' : 'Getting started'}
      </Button>
      {ready && onboarding.phase === 'stories' ? (
        <GameplayWorkspaceTour
          label="Welcome tour"
          finishLabel="Visit the Shop"
          steps={steps}
          onClose={(reason) => {
            if (reason === 'skip') onboarding.setPhase('done')
            else {
              onboarding.setPhase('shop')
              navigate(`${SHOP_ROUTE}?tab=companions`)
            }
          }}
        />
      ) : null}
    </>
  )
}
