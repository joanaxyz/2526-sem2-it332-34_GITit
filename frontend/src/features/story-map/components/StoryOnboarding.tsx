import { BookOpen, GitBranch, Play, Sparkles, Swords } from 'lucide-react'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { Modal } from '@/shared/components/Modal'
import { MascotMessage } from '@/shared/mascot/MascotMessage'
import { HOME_ROUTE, SHOP_ROUTE } from '@/shared/navigation/routes'

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
      title: 'This is your learning map',
      body: 'Choose a chapter, read its guide, then open a level. Practice runs use a safe workspace, never your real projects.',
    },
    {
      id: 'learn',
      selector: compact ? '[aria-controls="story-map-tools"]' : '.chapter-book',
      icon: BookOpen,
      title: 'Check the chapter guide',
      body: compact
        ? 'Open Chapter tools, then use the Field Guide to review the commands for this chapter.'
        : 'Open the Field Guide to review the commands for this chapter.',
    },
    {
      id: 'challenges',
      selector: '[data-onboarding="challenges"]',
      icon: Swords,
      title: 'Challenges follow practice',
      body: 'Finish the chapter’s Adventure levels to unlock its Challenge difficulties.',
      optional: true,
    },
    {
      id: 'play',
      selector: '[data-onboarding="next-level"]',
      icon: Play,
      title: 'Open your next level',
      body: 'Choose the glowing level, then select Play. The objective tells you what to do.',
      optional: true,
    },
    {
      id: 'companion',
      selector: compact ? '[aria-controls="story-map-utilities"]' : '.story-companion-panel',
      icon: Sparkles,
      title: hasCompanion ? 'Your companion is ready' : 'Choose a companion before playing',
      body: (compact ? 'Open Story utilities to see your companion. ' : '') + (hasCompanion
        ? 'Next, visit Home to see your profile and progress.'
        : 'Every playable level needs an equipped companion. Next, choose one in the Shop.'),
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
        title="Choose how to learn"
        className="story-onboarding-choice"
        contentClassName="story-onboarding-choice__content"
        onClose={skipOrientation}
      >
        <MascotMessage>
        <p>
          New to Git? Take the short primer. Already know the basics? Go to the first chapter.
        </p>
        <div className="story-onboarding-choice__actions">
          {orientationAvailable ? (
            <Button type="button" onClick={startOrientation}>Start Git primer</Button>
          ) : null}
          <Button type="button" variant="outline" onClick={skipOrientation}>
            Go to first chapter
          </Button>
        </div>
        <small>You can open the primer later from Chapters.</small>
        </MascotMessage>
      </Modal>

      {ready && onboarding.phase === 'stories' ? (
        <GameplayWorkspaceTour
          label="Getting started"
          finishLabel={hasCompanion ? 'Explore Home' : 'Choose a companion'}
          steps={steps}
          onClose={() => {
            if (hasCompanion) {
              onboarding.setPhase('home')
              navigate(HOME_ROUTE)
            } else {
              onboarding.setPhase('shop')
              navigate(`${SHOP_ROUTE}?required=1`)
            }
          }}
        />
      ) : null}
    </>
  )
}
