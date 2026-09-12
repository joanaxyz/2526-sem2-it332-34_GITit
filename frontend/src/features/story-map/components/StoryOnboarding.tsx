import { BookOpen, GitBranch, Play, Sparkles, Swords } from 'lucide-react'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { Modal } from '@/shared/components/Modal'
import { SHOP_ROUTE } from '@/shared/navigation/routes'

export function StoryOnboarding({
  ready,
  compact,
  hasCompanion,
  orientationAvailable,
  onStartOrientation,
  onSkipOrientation,
}: {
  ready: boolean
  compact: boolean
  hasCompanion: boolean
  orientationAvailable: boolean
  onStartOrientation: () => void
  onSkipOrientation: () => void
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

  function startOrientation() {
    onboarding!.setPhase('orientation')
    onStartOrientation()
  }

  function skipOrientation() {
    onboarding!.setPhase('stories')
    onSkipOrientation()
  }

  return (
    <>
      <Modal
        open={onboarding.phase === 'welcome'}
        title="Choose where to begin"
        className="story-onboarding-choice"
        contentClassName="story-onboarding-choice__content"
        onClose={skipOrientation}
      >
        <p>
          Module 0 is a guided introduction to Git and how GIT it! works. Take it if you are new to Git or want a refresher; otherwise, continue directly to Module 1.
        </p>
        <div className="story-onboarding-choice__actions">
          {orientationAvailable ? (
            <Button type="button" onClick={startOrientation}>I’m new — start Module 0</Button>
          ) : null}
          <Button type="button" variant="outline" onClick={skipOrientation}>
            I know the basics — skip to Module 1
          </Button>
        </div>
        <small>You can open Module 0 later from the Chapters dropdown.</small>
      </Modal>

      {ready && onboarding.phase === 'stories' ? (
        <GameplayWorkspaceTour
          label="Welcome tour"
          finishLabel="Visit the Shop"
          steps={steps}
          onClose={(reason) => {
            if (reason === 'skip') onboarding.setPhase('done')
            else {
              onboarding.setPhase('shop')
              navigate(SHOP_ROUTE)
            }
          }}
        />
      ) : null}
    </>
  )
}
