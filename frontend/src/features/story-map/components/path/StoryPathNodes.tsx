import { Check, Lock, Play, Swords } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { AdventureLevelSummary, AdventureLevelTierAccess } from '@/features/story-map/types'
import { adventureLevelCleared } from '@/features/story-map/utils/storyMapChapter'
import { StarRating, type StarFillState } from '@/shared/level/components/StarRating'

const DIFFICULTY_ORDER = ['easy', 'medium', 'hard'] as const

// Node-level star display only: one star per difficulty tier (easy/medium/
// hard, in that order), full once that tier is completed, half while a wave
// is in progress on it, empty otherwise. Distinct from the numeric `stars`
// grade used by the tier-popup and challenge-trial-card StarRating call
// sites, which this deliberately leaves untouched.
function tierStarFillStates(tiers: AdventureLevelTierAccess[]): StarFillState[] {
  return DIFFICULTY_ORDER.map((difficulty) => {
    const tier = tiers.find((candidate) => candidate.difficulty === difficulty)
    if (!tier) return 'empty'
    if (tier.completion) return 'full'
    if (tier.wave_progress.completed > 0 && tier.wave_progress.completed < tier.wave_progress.total) {
      return 'half'
    }
    return 'empty'
  })
}

type PathPoint = { x: number; y: number }

export function StoryPathLevelNode({
  level,
  index,
  position,
  chapterLocked,
  currentLevelId,
  loading,
  selectedLevelId,
  closingLevelId,
  onToggle,
  onOpenLevel,
}: {
  level?: AdventureLevelSummary
  index: number
  position: PathPoint
  chapterLocked: boolean
  currentLevelId: number | null
  loading: boolean
  selectedLevelId: number | null
  closingLevelId: number | null
  onToggle: (levelId: number) => void
  onOpenLevel: (level: AdventureLevelSummary) => void
}) {
  const state = level
    ? level.locked || chapterLocked
      ? 'locked'
      : adventureLevelCleared(level)
      ? 'cleared'
      : level.id === currentLevelId
      ? 'current'
      : 'ready'
    : loading
    ? 'loading'
    : 'locked'
  const hasTiers = Boolean(level && level.tiers.length > 0)
  const starFillStates = level && hasTiers ? tierStarFillStates(level.tiers) : undefined
  const stars = level?.completion?.stars ?? 0
  const disabled = !level || state === 'locked' || state === 'loading'
  const selected = Boolean(level && selectedLevelId === level.id)
  const closing = Boolean(level && closingLevelId === level.id && !selected)
  const showPlayPill = Boolean(level && !hasTiers && (selected || closing))

  return (
    <div
      className="story-path-node"
      data-state={state}
      data-selected={selected || undefined}
      style={{ '--node-x': `${position.x}px`, '--node-y': `${position.y}px` } as CSSProperties}
    >
      <button
        type="button"
        className="story-path-node-button"
        data-onboarding={level?.id === currentLevelId && !disabled ? 'next-level' : undefined}
        disabled={disabled}
        aria-label={
          level
            ? `Level ${index + 1}: ${level.title}. ${selected ? 'Play action open' : 'Open play action'}.`
            : `Locked level ${index + 1}`
        }
        aria-expanded={level ? selected : undefined}
        aria-controls={level && hasTiers ? 'story-level-tier-panel' : undefined}
        onClick={() => {
          if (level) onToggle(level.id)
        }}
      >
        <span className="story-path-node-ring">
          {state === 'locked' ? <Lock className="size-5" aria-hidden="true" /> : <span>{index + 1}</span>}
        </span>
        {state === 'cleared' ? (
          <span className="story-path-node-badge" aria-hidden="true">
            <Check className="size-3.5" strokeWidth={3} />
          </span>
        ) : null}
      </button>

      {showPlayPill ? (
        <button
          type="button"
          className="story-path-node-play"
          data-pill-state={closing ? 'closing' : 'open'}
          aria-label={`Play ${level!.title}`}
          onClick={() => onOpenLevel(level!)}
        >
          <Play className="size-4" fill="currentColor" aria-hidden="true" />
          <span className="sr-only">Play</span>
        </button>
      ) : null}

      {state === 'locked' || state === 'loading' ? null : (
        <StarRating
          stars={starFillStates ? undefined : stars}
          fillStates={starFillStates}
          size="sm"
          className="story-path-stars"
          label={level?.title ?? 'Level'}
        />
      )}
    </div>
  )
}

export type StoryTrialState = 'loading' | 'locked' | 'cleared' | 'ready'

export function StoryChallengeNode({
  trialCount,
  state,
  open,
  disabled,
  position,
  loading,
  chapterLocked,
  chapterLockReason,
  onToggle,
}: {
  trialCount: number
  state: StoryTrialState
  open: boolean
  disabled: boolean
  position: PathPoint
  loading: boolean
  chapterLocked: boolean
  chapterLockReason: string
  onToggle: () => void
}) {
  return (
    <button
      type="button"
      className="story-path-node story-path-node--trial"
      data-onboarding={trialCount > 0 ? 'challenges' : undefined}
      data-state={state}
      data-open={open || undefined}
      style={{ '--node-x': `${position.x}px`, '--node-y': `${position.y}px` } as CSSProperties}
      disabled={disabled}
      title={
        state === 'locked' && !loading
          ? chapterLocked
            ? chapterLockReason
            : 'Clear the adventure levels to unlock the trials.'
          : undefined
      }
      aria-label={state === 'locked' ? 'Challenge trials (locked)' : 'Challenge trials'}
      aria-expanded={open}
      aria-controls="story-challenge-panel"
      onClick={onToggle}
    >
      <span className="story-path-node-ring">
        {state === 'locked' ? (
          <Lock className="size-5" aria-hidden="true" />
        ) : (
          <Swords className="size-6" aria-hidden="true" />
        )}
      </span>
      <span className="story-challenge-node-label">Challenge Gate</span>
      {state === 'cleared' ? (
        <span className="story-path-node-badge" aria-hidden="true">
          <Check className="size-3.5" strokeWidth={3} />
        </span>
      ) : null}
    </button>
  )
}
