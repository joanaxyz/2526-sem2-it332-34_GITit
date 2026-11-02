import { BookOpen, GitBranch } from 'lucide-react'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { Modal } from '@/shared/components/Modal'
import { MascotMessage } from '@/shared/mascot/MascotMessage'
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
      title: 'This is your learning map',
      body: 'Choose a chapter and open a level. Practice runs use a safe workspace — never your real projects.',
    },
    {
      id: 'learn',
      selector: compact ? '[aria-controls="story-map-tools"]' : '.chapter-book',
      icon: BookOpen,
      title: 'Open the Field Guide',
      body: compact
        ? 'Open Chapter tools, then use the Field Guide to review the Git commands for this chapter before you play.'
        : 'Open the Field Guide to review the Git commands for this chapter before you play.',
    },
  ] satisfies WorkspaceTourStep[], [compact])

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
          New to Git? Start with the short primer. Already know the basics? Jump straight to the first chapter.
        </p>
        <div className="story-onboarding-choice__actions">
          {orientationAvailable ? (
            <Button type="button" onClick={startOrientation}>Start Git primer</Button>
          ) : null}
          <Button type="button" variant="outline" onClick={skipOrientation}>
            Go to first chapter
          </Button>
        </div>
        <small>You can open the primer anytime from the Chapters panel.</small>
        </MascotMessage>
      </Modal>

      {ready && onboarding.phase === 'stories' ? (
        <GameplayWorkspaceTour
          label="Getting started"
          finishLabel={hasCompanion ? 'Start playing' : 'Choose a companion'}
          steps={steps}
          onClose={() => {
            if (hasCompanion) {
              onboarding.setPhase('done')
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
