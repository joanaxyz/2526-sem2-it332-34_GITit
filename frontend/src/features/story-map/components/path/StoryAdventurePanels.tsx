import { Lock, Swords } from 'lucide-react'
import type { CSSProperties, RefObject } from 'react'

import easyIconImage from '@/assets/images/easy_icon.png'
import hardIconImage from '@/assets/images/hard_icon.png'
import mediumIconImage from '@/assets/images/medium_icon.png'
import type {
  AdventureLevelSummary,
  ChallengeSummary,
} from '@/features/story-map/types'
import {
  actionForChallengeLevel,
  actionLabel,
  challengeLevelAccent,
  difficultyLabel,
} from '@/features/story-map/utils/challengeUi'
import { StarRating } from '@/shared/level/components/StarRating'

const DIFFICULTY_ORDER = ['easy', 'medium', 'hard'] as const

const DIFFICULTY_ICONS: Record<(typeof DIFFICULTY_ORDER)[number], string> = {
  easy: easyIconImage,
  medium: mediumIconImage,
  hard: hardIconImage,
}

const DIFFICULTY_TIER_LABELS: Record<(typeof DIFFICULTY_ORDER)[number], string> = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
}

export function StoryLevelTierPanel({
  level,
  panelRef,
  style,
  pendingTierId,
  isStarting,
  onStartTier,
}: {
  level: AdventureLevelSummary
  panelRef: RefObject<HTMLElement | null>
  style: CSSProperties
  pendingTierId?: number
  isStarting: boolean
  onStartTier: (tierId: number, replay: boolean) => void
}) {
  return (
    <section
      id="story-level-tier-panel"
      ref={panelRef}
      className="story-level-tier-panel"
      style={style}
      aria-labelledby="story-level-tier-panel-title"
    >
      <header className="story-level-tier-panel-header">
        <h2 id="story-level-tier-panel-title">{level.title}</h2>
        <p>{level.description}</p>
      </header>

      <div className="story-level-tier-panel-list">
        {DIFFICULTY_ORDER.map((difficulty) => {
          const tier = level.tiers.find((item) => item.difficulty === difficulty)
          const isLocked = !tier || tier.locked
          const isCleared = Boolean(tier?.completion)
          const stars = tier?.completion?.stars ?? 0
          const progress = tier?.wave_progress ?? { completed: 0, total: 0 }
          const status = isLocked
            ? 'locked'
            : isCleared
              ? 'cleared'
              : progress.completed > 0
                ? 'in_progress'
                : 'not_started'
          const nextActionLabel =
            status === 'cleared' ? 'Review' : status === 'in_progress' ? 'Continue' : 'Start'
          const isStartingThisTier = isStarting && pendingTierId === tier?.id

          return (
            <button
              type="button"
              className="story-level-tier-card"
              data-status={status}
              key={`${level.id}-${difficulty}`}
              disabled={isLocked || !tier || isStarting}
              aria-label={`${level.title}: ${difficulty} tier. ${nextActionLabel}.`}
              title={isLocked ? 'Clear the previous difficulty to unlock this tier.' : undefined}
              onClick={() => {
                if (!tier || isLocked) return
                onStartTier(tier.id, isCleared)
              }}
            >
              <span className="story-level-tier-card-medallion">
                <img src={DIFFICULTY_ICONS[difficulty]} alt="" />
                {isLocked ? <Lock className="story-trial-lock" aria-hidden="true" /> : null}
              </span>
              <span className="story-level-tier-card-copy">
                <strong>{DIFFICULTY_TIER_LABELS[difficulty]}</strong>
                <StarRating stars={stars} size="sm" label={`${difficulty} stars`} />
              </span>
              {isLocked ? (
                <span className="story-level-tier-card-progress">
                  {progress.completed}/{progress.total}
                </span>
              ) : (
                <span className="story-level-tier-card-cta">
                  <span className="story-level-tier-card-action">
                    {isStartingThisTier ? 'Starting…' : nextActionLabel}
                  </span>
                  <span className="story-level-tier-card-progress">
                    {progress.completed}/{progress.total}
                  </span>
                </span>
              )}
            </button>
          )
        })}
      </div>
    </section>
  )
}

export function StoryTrialsPanel({
  challenges,
  challengesLocked,
  clearedTrialCount,
  loading,
  panelRef,
  trialCount,
  onOpenTrial,
}: {
  challenges: ChallengeSummary[]
  challengesLocked: boolean
  clearedTrialCount: number
  loading: boolean
  panelRef: RefObject<HTMLElement | null>
  trialCount: number
  onOpenTrial: (
    trial: ChallengeSummary['trials'][number],
    action: NonNullable<ReturnType<typeof actionForChallengeLevel>>,
  ) => void
}) {
  return (
    <section
      id="story-challenge-panel"
      ref={panelRef}
      className="story-trials-panel"
      aria-labelledby="story-challenge-panel-title"
    >
      <header className="story-trials-panel-header">
        <span className="story-trials-panel-mark" aria-hidden="true">
          <Swords />
        </span>
        <div>
          <h2 id="story-challenge-panel-title">Challenge Gate</h2>
          <p>Clear each trial to master the chapter.</p>
        </div>
        <span className="story-trials-panel-progress">
          {clearedTrialCount} / {trialCount} cleared
        </span>
      </header>

      <div className="story-trials-panel-content">
        {challenges.map((challenge) => (
          <section
            className="story-trials-group"
            key={challenge.id}
            aria-labelledby={`challenge-${challenge.id}-title`}
          >
            <h3 id={`challenge-${challenge.id}-title`} className="story-trials-group-title">
              {challenge.title}
            </h3>
            <div className="story-trials-grid">
              {DIFFICULTY_ORDER.map((difficulty) => {
                const trial =
                  challenge.trials.find((item) => String(item.difficulty) === difficulty) ?? null
                const action = trial ? actionForChallengeLevel(trial) : null
                const isLocked = challengesLocked || !trial || !action || trial.status === 'locked'
                const status = loading ? 'loading' : isLocked ? 'locked' : trial.status
                const stars = trial?.completion?.stars ?? 0
                const accent = challengeLevelAccent(trial)

                return (
                  <button
                    type="button"
                    className="story-trial-card"
                    data-status={status}
                    key={`${challenge.id}-${difficulty}`}
                    disabled={isLocked || loading}
                    style={{ '--trial-rgb': accent } as CSSProperties}
                    aria-label={`${challenge.title}: ${difficulty} challenge trial`}
                    onClick={() => {
                      if (!trial || !action) return
                      onOpenTrial(trial, action)
                    }}
                  >
                    <span className="story-trial-medallion">
                      <img src={DIFFICULTY_ICONS[difficulty]} alt="" />
                      {status === 'locked' || status === 'loading' ? (
                        <Lock className="story-trial-lock" aria-hidden="true" />
                      ) : null}
                    </span>
                    <span className="story-trial-copy">
                      <strong>{trial ? difficultyLabel(trial) : difficulty}</strong>
                      <StarRating stars={stars} size="sm" label={`${difficulty} stars`} />
                      <span>{trial ? actionLabel(action, trial.status) : 'Locked'}</span>
                    </span>
                  </button>
                )
              })}
            </div>
          </section>
        ))}
      </div>
    </section>
  )
}
