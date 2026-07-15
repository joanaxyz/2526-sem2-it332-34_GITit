import { Check, Lock, Play } from 'lucide-react'
import { useMemo } from 'react'

import type { AdventureSummary } from '@/features/challenges/types'
import { useStoryArtifactNavigation } from '@/features/story-map/hooks/useStoryArtifactNavigation'
import { adventureLevelCleared } from '@/features/story-map/utils/storyMapChapter'
import { Modal } from '@/shared/components/Modal'
import { StarRating } from '@/shared/level/components/StarRating'

type LevelState = 'cleared' | 'current' | 'ready' | 'locked'

export function AdventureLevelsModal({
  adventures,
  locked,
  lockReason,
  onClose,
}: {
  adventures: AdventureSummary[]
  locked?: boolean
  lockReason?: string
  onClose: () => void
}) {
  const { openAdventureLevel } = useStoryArtifactNavigation()
  const tally = useMemo(() => clearedTally(adventures), [adventures])
  const currentLevelId = useMemo(() => nextPlayableLevelId(adventures, Boolean(locked)), [adventures, locked])

  return (
    <Modal
      open
      title="Adventure Levels"
      onClose={onClose}
      className="content-viewbox-modal"
      contentClassName="content-viewbox-modal-body app-scrollbar"
      overlayClassName="story-content-modal-overlay"
    >
      <div className="ls">
        <header className="ls-head">
          <p className="ls-eyebrow">Adventure path</p>
          <p className="ls-head-count">
            <strong>{tally.cleared}</strong>
            <span>/ {tally.total} levels cleared</span>
          </p>
        </header>

        <div className="ls-worlds">
          <section className="ls-world">
            <ol className="ls-grid ls-grid--levels">
              {adventures.map((level, index) => {
                const state = levelState(level, Boolean(locked), level.id === currentLevelId)
                const isLocked = state === 'locked'
                const stars = level.completion?.stars ?? 0
                return (
                  <li key={level.id}>
                    <button
                      type="button"
                      className="ls-node ls-node--level"
                      data-state={state}
                      disabled={isLocked}
                      title={isLocked ? level.lock_reason || lockReason : undefined}
                      aria-label={`Level ${index + 1}: ${level.title}. ${STATE_LABEL[state]}. ${stars} of 3 stars.`}
                      onClick={() => {
                        openAdventureLevel(level)
                        onClose()
                      }}
                    >
                      <span
                        className="ls-ring"
                        style={{ '--pct': state === 'cleared' ? 100 : 0 } as React.CSSProperties}
                      >
                        <span className="ls-ring-core">
                          {isLocked ? (
                            <Lock className="ls-ring-icon" aria-hidden="true" />
                          ) : (
                            <span className="ls-num">{index + 1}</span>
                          )}
                        </span>
                        {state === 'cleared' ? (
                          <span className="ls-badge ls-badge--done" aria-hidden="true">
                            <Check className="size-3" strokeWidth={3} />
                          </span>
                        ) : null}
                        {state === 'current' ? (
                          <span className="ls-badge ls-badge--go" aria-hidden="true">
                            <Play className="size-3" strokeWidth={2.5} />
                          </span>
                        ) : null}
                      </span>

                      <span className="ls-node-title">{level.title}</span>
                      <span className="ls-node-foot" data-state={state}>
                        {STATE_LABEL[state]}
                      </span>
                      <StarRating stars={stars} size="sm" label={`${level.title} stars`} />
                      <span className="ls-strip" aria-hidden="true" data-filled={state === 'cleared'} />
                    </button>
                  </li>
                )
              })}
            </ol>
          </section>
        </div>

        {locked ? (
          <p className="ls-lock">
            <Lock className="size-3.5" />
            {lockReason || 'Clear the previous chapter to unlock.'}
          </p>
        ) : null}
      </div>
    </Modal>
  )
}

const STATE_LABEL: Record<LevelState, string> = {
  cleared: 'Cleared',
  current: 'Play',
  ready: 'Play',
  locked: 'Locked',
}

function levelState(level: AdventureSummary, modalLocked: boolean, isCurrent: boolean): LevelState {
  if (level.locked || modalLocked) return 'locked'
  if (adventureLevelCleared(level)) return 'cleared'
  if (isCurrent) return 'current'
  return 'ready'
}

function nextPlayableLevelId(adventures: AdventureSummary[], modalLocked: boolean): number | null {
  const playable = adventures.filter((level) => !modalLocked && !level.locked && !adventureLevelCleared(level))
  return playable[0]?.id ?? null
}

function clearedTally(adventures: AdventureSummary[]) {
  return {
    cleared: adventures.filter(adventureLevelCleared).length,
    total: adventures.length,
  }
}
