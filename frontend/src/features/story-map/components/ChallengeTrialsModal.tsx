import { Lock } from 'lucide-react'

import type { ChallengeSummary, ChallengeTrialAccess } from '@/features/challenges/types'
import {
  actionForChallengeLevel,
  actionLabel,
  challengeLevelAccent,
  difficultyLabel,
} from '@/features/story-map/utils/challengeUi'
import { useStoryArtifactNavigation } from '@/features/story-map/hooks/useStoryArtifactNavigation'
import { Modal } from '@/shared/components/Modal'
import { StarRating } from '@/shared/level/components/StarRating'

const DIFFICULTY_ORDER = ['easy', 'medium', 'hard'] as const

const STATUS_LABEL: Record<ChallengeTrialAccess['status'], string> = {
  not_started: 'Play',
  locked: 'Locked',
  in_progress: 'Play',
  completed: 'Cleared',
  failed: 'Retry',
  abandoned: 'Retry',
}

export function ChallengeTrialsModal({
  challenges,
  locked,
  lockReason,
  onClose,
}: {
  challenges: ChallengeSummary[]
  locked: boolean
  lockReason?: string
  onClose: () => void
}) {
  const { openChallengeArtifact } = useStoryArtifactNavigation()
  const tally = aggregateChallengeTally(challenges)
  const title = challenges.length === 1 ? challenges[0].title : 'Challenges'

  return (
    <Modal
      open
      title={title}
      onClose={onClose}
      className="content-viewbox-modal"
      contentClassName="content-viewbox-modal-body app-scrollbar"
      overlayClassName="story-content-modal-overlay"
    >
      <div className="ls">
        <header className="ls-head">
          <p className="ls-eyebrow">Trial gauntlet</p>
          <p className="ls-head-count">
            <strong>{tally.cleared}</strong>
            <span>/ {tally.total} trials cleared</span>
          </p>
        </header>

        {locked ? (
          <p className="ls-lock">
            <Lock className="size-3.5" />
            {lockReason || 'Clear this chapter’s adventure levels to unlock these trials.'}
          </p>
        ) : null}

        <div className="ls-worlds">
          {challenges.map((challenge, index) => {
            const trial = challengeTally(challenge)
            return (
              <section key={challenge.id} className="ls-world ls-world--trial">
                <div className="ls-trial-head">
                  <div className="ls-trial-copy min-w-0">
                    <span className="ls-eyebrow">Challenge {index + 1}</span>
                    <h3>{challenge.title}</h3>
                    {challenge.summary ? <p>{challenge.summary}</p> : null}
                  </div>
                  <span className="ls-trial-count">
                    <strong>{trial.cleared}</strong>/{trial.total}
                  </span>
                </div>

                <div className="ls-grid ls-grid--trio" aria-label={`${challenge.title} difficulties`}>
                  {orderedTrialLevels(challengeTrials(challenge)).map((level) => {
                    const action = actionForChallengeLevel(level)
                    const disabled = locked || !action
                    const accent = challengeLevelAccent(level)
                    const isDone = level.status === 'completed'
                    const ringPct = isDone ? 100 : 0
                    const stars = level.completion?.stars ?? 0
                    const buttonLabel = action
                      ? actionLabel(action, level.status)
                      : STATUS_LABEL[level.status]

                    return (
                      <button
                        key={level.id}
                        type="button"
                        className="ls-node ls-node--trial"
                        data-difficulty={String(level.difficulty)}
                        data-status={level.status}
                        disabled={disabled}
                        style={{ '--ring-rgb': accent } as React.CSSProperties}
                        aria-label={`${difficultyLabel(level)}. ${buttonLabel}. ${stars} of 3 stars.`}
                        onClick={() => {
                          if (!action) return
                          openChallengeArtifact(level, action)
                          onClose()
                        }}
                      >
                        <span className="ls-ring" style={{ '--pct': ringPct } as React.CSSProperties}>
                          <span className="ls-ring-core">
                            {level.status === 'locked' ? (
                              <Lock className="ls-ring-icon" aria-hidden="true" />
                            ) : (
                              <span className="ls-num">{difficultyLabel(level).slice(0, 1)}</span>
                            )}
                          </span>
                        </span>

                        <span className="ls-node-title">{difficultyLabel(level)}</span>
                        <span className="ls-node-foot" data-status={level.status} data-done={isDone}>
                          {buttonLabel}
                        </span>
                        <StarRating stars={stars} size="sm" label={`${difficultyLabel(level)} stars`} />
                      </button>
                    )
                  })}
                </div>
              </section>
            )
          })}
        </div>
      </div>
    </Modal>
  )
}

function orderedTrialLevels(levels: ChallengeTrialAccess[]) {
  return [...levels].sort((a, b) => difficultySortKey(a) - difficultySortKey(b))
}

function difficultySortKey(level: ChallengeTrialAccess) {
  const knownIndex = DIFFICULTY_ORDER.indexOf(String(level.difficulty) as (typeof DIFFICULTY_ORDER)[number])
  return knownIndex === -1 ? DIFFICULTY_ORDER.length : knownIndex
}

function aggregateChallengeTally(challenges: ChallengeSummary[]) {
  const levels = challenges.flatMap((challenge) => challengeTrials(challenge))
  return {
    cleared: levels.filter((level) => level.status === 'completed').length,
    total: levels.length,
  }
}

function challengeTally(challenge: ChallengeSummary) {
  const trials = challengeTrials(challenge)
  return {
    cleared: trials.filter((level) => level.status === 'completed').length,
    total: trials.length,
  }
}

function challengeTrials(challenge: ChallengeSummary) {
  return challenge.trials
}
