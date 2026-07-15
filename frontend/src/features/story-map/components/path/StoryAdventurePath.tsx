import { useEffect, useMemo, useRef, useState } from 'react'
import { Check, Lock, Play, Swords } from 'lucide-react'

import type { AdventureLevelSummary, ChallengeSummary } from '@/features/challenges/types'
import {
  actionForChallengeLevel,
  actionLabel,
  allChallengeTrials,
  challengeLevelAccent,
  difficultyLabel,
} from '@/features/story-map/utils/challengeUi'
import { pathDataFor, pathGeometry, trialFlyoutPlacement } from '@/features/story-map/utils/pathGeometry'
import { useStoryArtifactNavigation } from '@/features/story-map/hooks/useStoryArtifactNavigation'
import type { LearningChapter } from '@/features/story-map/types'
import { StarRating } from '@/shared/level/components/StarRating'

import easyIconImage from '@/assets/images/easy_icon.png'
import hardIconImage from '@/assets/images/hard_icon.png'
import mediumIconImage from '@/assets/images/medium_icon.png'
import { adventureLevelCleared, nextPlayableLevelId } from '@/features/story-map/utils/storyMapChapter'

const DIFFICULTY_ORDER = ['easy', 'medium', 'hard'] as const
const DIFFICULTY_ICONS: Record<(typeof DIFFICULTY_ORDER)[number], string> = {
  easy: easyIconImage,
  medium: mediumIconImage,
  hard: hardIconImage,
}

const PILL_CLOSE_MS = 180

export function StoryAdventurePath({
  chapter,
  levels,
  challenges,
  challengesLocked,
  loading,
}: {
  chapter: LearningChapter
  levels: AdventureLevelSummary[]
  challenges: ChallengeSummary[]
  challengesLocked: boolean
  loading: boolean
}) {
  const { openAdventureLevel, openChallengeArtifact } = useStoryArtifactNavigation()
  const currentLevelId = nextPlayableLevelId(levels, chapter.locked)
  const placeholderCount = Math.max(3, chapter.adventure_level_count || 6)
  const nodes: Array<AdventureLevelSummary | undefined> = levels.length
    ? levels
    : Array.from({ length: placeholderCount })
  const trials = allChallengeTrials(challenges)
  const [trialsOpen, setTrialsOpen] = useState(false)
  const [selectedLevelId, setSelectedLevelId] = useState<number | null>(null)
  const [closingLevelId, setClosingLevelId] = useState<number | null>(null)
  const closeTimerRef = useRef<number | null>(null)

  const pathRef = useRef<HTMLDivElement | null>(null)
  const [pathWidth, setPathWidth] = useState(640)
  useEffect(() => {
    const el = pathRef.current
    if (!el) return
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width ?? 0
      if (width > 0) setPathWidth(Math.max(320, Math.min(720, Math.round(width))))
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  function queueClosingPill(levelId: number) {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    setClosingLevelId(levelId)
    closeTimerRef.current = window.setTimeout(() => {
      setClosingLevelId((current) => (current === levelId ? null : current))
      closeTimerRef.current = null
    }, PILL_CLOSE_MS)
  }

  function toggleLevelPill(levelId: number) {
    if (selectedLevelId === levelId) {
      queueClosingPill(levelId)
      setSelectedLevelId(null)
      return
    }
    if (selectedLevelId !== null) queueClosingPill(selectedLevelId)
    setClosingLevelId((closing) => (closing === levelId ? null : closing))
    setSelectedLevelId(levelId)
  }

  useEffect(() => {
    setTrialsOpen(false)
    setSelectedLevelId(null)
    setClosingLevelId(null)
  }, [chapter.id])

  useEffect(() => {
    if (selectedLevelId && !levels.some((level) => level.id === selectedLevelId && !level.locked)) {
      setSelectedLevelId(null)
    }
  }, [levels, selectedLevelId])

  useEffect(() => {
    return () => {
      if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    }
  }, [])

  useEffect(() => {
    if (!trialsOpen) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setTrialsOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [trialsOpen])

  // One extra point: the chapter's challenge trials live on the same path,
  // as its final node.
  const { points, height } = useMemo(
    () => pathGeometry(nodes.length + 1, pathWidth),
    [nodes.length, pathWidth],
  )
  const routePathData = useMemo(() => pathDataFor(points), [points])
  const trialPoint = points[points.length - 1]

  const trialsCleared = trials.length > 0 && trials.every((trial) => trial.completion)
  const trialState = loading
    ? 'loading'
    : challengesLocked || !trials.length
    ? 'locked'
    : trialsCleared
    ? 'cleared'
    : 'ready'
  const trialDisabled = trialState === 'locked' || trialState === 'loading'

  const {
    left: flyoutLeft,
    top: flyoutTop,
    connectors: trialConnectors,
  } = trialFlyoutPlacement(trialPoint, pathWidth, height)

  return (
    <div className="story-adventure-path" ref={pathRef}>
      <div className="story-path-canvas" style={{ width: pathWidth, height }}>
        <svg
          className="story-route-line"
          viewBox={`0 0 ${pathWidth} ${height}`}
          width={pathWidth}
          height={height}
          aria-hidden="true"
          focusable="false"
        >
          <path d={routePathData} />
          {trialsOpen
            ? trialConnectors.map((d) => <path className="story-route-branch" d={d} key={d} />)
            : null}
        </svg>

        {nodes.map((node, index) => {
          const level = node
          const pos = points[index]
          const state = level
            ? level.locked || chapter.locked
              ? 'locked'
              : adventureLevelCleared(level)
              ? 'cleared'
              : level.id === currentLevelId
              ? 'current'
              : 'ready'
            : loading
            ? 'loading'
            : 'locked'
          const stars = level?.completion?.stars ?? 0
          const disabled = !level || state === 'locked' || state === 'loading'
          const selected = Boolean(level && selectedLevelId === level.id)
          const closing = Boolean(level && closingLevelId === level.id && !selected)
          const showPlayPill = Boolean(level && (selected || closing))

          return (
            <div
              className="story-path-node"
              data-state={state}
              data-selected={selected || undefined}
              key={level?.id ?? `placeholder-${index}`}
              style={{ '--node-x': `${pos.x}px`, '--node-y': `${pos.y}px` } as React.CSSProperties}
            >
              <button
                type="button"
                className="story-path-node-button"
                disabled={disabled}
                aria-label={
                  level
                    ? `Level ${index + 1}: ${level.title}. ${selected ? 'Play action open' : 'Open play action'}.`
                    : `Locked level ${index + 1}`
                }
                aria-expanded={level ? selected : undefined}
                onClick={() => {
                  if (!level) return
                  toggleLevelPill(level.id)
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
                  onClick={() => openAdventureLevel(level!)}
                >
                  <Play className="size-4" fill="currentColor" aria-hidden="true" />
                  <span className="sr-only">Play</span>
                </button>
              ) : null}

              {state === 'locked' || state === 'loading' ? null : (
                <StarRating stars={stars} size="sm" className="story-path-stars" label={level?.title ?? 'Level'} />
              )}
            </div>
          )
        })}

        <button
          type="button"
          className="story-path-node story-path-node--trial"
          data-state={trialState}
          data-open={trialsOpen || undefined}
          style={{ '--node-x': `${trialPoint.x}px`, '--node-y': `${trialPoint.y}px` } as React.CSSProperties}
          disabled={trialDisabled}
          title={
            trialState === 'locked' && !loading
              ? chapter.locked
                ? chapter.lock_reason
                : 'Clear the adventure levels to unlock the trials.'
              : undefined
          }
          aria-label={trialState === 'locked' ? 'Challenge trials (locked)' : 'Challenge trials'}
          aria-expanded={trialsOpen}
          aria-controls="story-trials-flyout"
          onClick={() => setTrialsOpen((open) => !open)}
        >
          <span className="story-path-node-ring">
            {trialState === 'locked' ? (
              <Lock className="size-5" aria-hidden="true" />
            ) : (
              <Swords className="size-6" aria-hidden="true" />
            )}
          </span>
          {trialState === 'cleared' ? (
            <span className="story-path-node-badge" aria-hidden="true">
              <Check className="size-3.5" strokeWidth={3} />
            </span>
          ) : null}
        </button>

        {trialsOpen ? (
          <div
            id="story-trials-flyout"
            className="story-trials-flyout"
            style={{ left: flyoutLeft, top: flyoutTop }}
            role="group"
            aria-label="Challenge trials"
          >
            {/* One section per challenge level: a chapter can carry several
                challenge scenarios, and every trial of each must stay reachable. */}
            {challenges.map((challenge) => (
              <div className="story-trials-flyout-group" key={challenge.id} role="group" aria-label={challenge.title}>
                {challenges.length > 1 ? (
                  <span className="story-trials-flyout-title">{challenge.title}</span>
                ) : null}
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
                      style={{ '--trial-rgb': accent } as React.CSSProperties}
                      aria-label={`${challenge.title}: ${difficulty} challenge trial`}
                      onClick={() => {
                        if (!trial || !action) return
                        openChallengeArtifact(trial, action)
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
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}
