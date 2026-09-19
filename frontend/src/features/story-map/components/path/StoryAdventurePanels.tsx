import { Lock, Swords, X } from 'lucide-react'
import type { CSSProperties, RefObject } from 'react'

import easyIconImage from '@/assets/images/easy_icon.png'
import hardIconImage from '@/assets/images/hard_icon.png'
import mediumIconImage from '@/assets/images/medium_icon.png'
import type {
  AdventureLevelSummary,
  AdventureLevelTierAccess,
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

export type LevelTierRowStatus = 'locked' | 'cleared' | 'in_progress' | 'not_started'

const TIER_ACTION_LABELS: Record<Exclude<LevelTierRowStatus, 'locked'>, string> = {
  cleared: 'Review',
  in_progress: 'Continue',
  not_started: 'Start',
}

function tierRowStatus(tier: AdventureLevelTierAccess | undefined): LevelTierRowStatus {
  if (!tier || tier.locked) return 'locked'
  if (tier.completion) return 'cleared'
  return tier.wave_progress.completed > 0 ? 'in_progress' : 'not_started'
}

/** The level callout: a level node's title, brief, and one row per difficulty
 *  tier. `placement` is 'docked' when it is absolutely positioned in the
 *  canvas gutter beside its node, 'inline' when the canvas is too narrow for
 *  a gutter and it falls into document flow under the path instead. */
export function StoryLevelTierPanel({
  level,
  levelNumber,
  panelRef,
  placement,
  style,
  pendingTierId,
  isStarting,
  onClose,
  onStartTier,
  onOpenDrill,
}: {
  level: AdventureLevelSummary
  levelNumber: number
  panelRef: RefObject<HTMLElement | null>
  placement: 'docked' | 'inline'
  style?: CSSProperties
  pendingTierId?: number
  isStarting: boolean
  onClose: () => void
  onStartTier: (tierId: number, replay: boolean) => void
  onOpenDrill: () => void
}) {
  const rows = DIFFICULTY_ORDER.map((difficulty) => {
    const tier = level.tiers.find((item) => item.difficulty === difficulty)
    return { difficulty, tier, status: tierRowStatus(tier) }
  })
  // Exactly one accent action per callout: the first tier that is unlocked
  // and unfinished. Everything else is a review or a lock, so the primary
  // move is unambiguous without reading a word.
  const nextDifficulty = rows.find(
    (row) => row.status === 'in_progress' || row.status === 'not_started',
  )?.difficulty
  // Defaulted, not assumed: a cached overview written before the drill
  // shipped has no `drill` key, and a level callout must not throw because
  // an optional feature is missing from a stale payload.
  const drill = level.drill ?? { available: false, cleared: false, best_accuracy: 0 }
  // Squire's Drill is the rung before the tiers, so it takes the callout's
  // one accent only while it is genuinely the best next move: nothing here
  // cleared yet, and the drill not done. Once either is true the accent
  // belongs to the tier again, and the drill demotes to a quiet re-entry.
  const drillIsNextMove =
    drill.available && !drill.cleared && !rows.some((row) => row.status === 'cleared')

  return (
    <section
      id="story-level-tier-panel"
      ref={panelRef}
      className="story-level-callout"
      data-placement={placement}
      style={style}
      aria-labelledby="story-level-tier-panel-title"
    >
      <header className="story-level-callout-head">
        <p className="story-level-callout-eyebrow">Level {String(levelNumber).padStart(2, '0')}</p>
        <h2 id="story-level-tier-panel-title">{level.title}</h2>
        {level.description ? (
          <p className="story-level-callout-brief">{level.description}</p>
        ) : null}
        <button
          type="button"
          className="story-level-callout-close"
          aria-label={`Close ${level.title} details`}
          onClick={onClose}
        >
          <X aria-hidden="true" />
        </button>
      </header>

      {drill.available ? (
        <button
          type="button"
          className="story-level-drill-row"
          data-next={drillIsNextMove || undefined}
          data-cleared={drill.cleared || undefined}
          aria-label={
            drill.cleared
              ? `Squire's Drill for ${level.title}: cleared, best ${drill.best_accuracy} percent. Drill again.`
              : `Squire's Drill for ${level.title}: rehearse this level's commands.`
          }
          onClick={onOpenDrill}
        >
          <span className="story-level-drill-rune" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
          <span className="story-level-drill-copy">
            <strong>Squire&rsquo;s Drill</strong>
            <span className="story-level-drill-meta">
              {drill.cleared ? (
                <>
                  Cleared · <b>{drill.best_accuracy}%</b> best
                </>
              ) : (
                "Rehearse this level's commands"
              )}
            </span>
          </span>
          <span className="story-level-tier-row-action">
            {drill.cleared ? 'Again' : 'Drill'}
          </span>
        </button>
      ) : null}

      <ul className="story-level-tier-rows">
        {rows.map(({ difficulty, tier, status }, index) => {
          const tierLabel = DIFFICULTY_TIER_LABELS[difficulty]
          const progress = tier?.wave_progress ?? { completed: 0, total: 0 }
          const isLocked = status === 'locked'
          const isStartingThisTier = isStarting && pendingTierId === tier?.id
          const actionLabel = isLocked
            ? 'Locked'
            : isStartingThisTier
              ? 'Starting…'
              : TIER_ACTION_LABELS[status]

          return (
            <li key={`${level.id}-${difficulty}`}>
              <button
                type="button"
                className="story-level-tier-row"
                data-status={status}
                data-next={(!drillIsNextMove && difficulty === nextDifficulty) || undefined}
                style={{ '--row-index': index } as CSSProperties}
                disabled={isLocked || !tier || isStarting}
                aria-label={`${level.title}, ${tierLabel} tier: ${actionLabel}`}
                title={isLocked ? 'Clear the previous difficulty to unlock this tier.' : undefined}
                onClick={() => {
                  if (!tier || isLocked) return
                  onStartTier(tier.id, status === 'cleared')
                }}
              >
                <span className="story-level-tier-row-mark">
                  <img src={DIFFICULTY_ICONS[difficulty]} alt="" />
                </span>
                <span className="story-level-tier-row-copy">
                  <strong>{tierLabel}</strong>
                  <span className="story-level-tier-row-meta">
                    {isLocked ? null : (
                      <StarRating
                        stars={tier?.completion?.stars ?? 0}
                        size="sm"
                        label={`${tierLabel} stars`}
                      />
                    )}
                    {progress.total > 0
                      ? isLocked
                        ? `${progress.total} ${progress.total === 1 ? 'wave' : 'waves'}`
                        : `${progress.completed}/${progress.total}`
                      : null}
                  </span>
                </span>
                {isLocked ? (
                  <Lock className="story-level-tier-row-lock" aria-hidden="true" />
                ) : (
                  <span className="story-level-tier-row-action">{actionLabel}</span>
                )}
              </button>
            </li>
          )
        })}
      </ul>
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
