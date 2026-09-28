import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { AdventureLevelSummary, ChallengeSummary } from '@/features/story-map/types'
import { allChallengeTrials } from '@/features/story-map/utils/challengeUi'
import { pathDataFor, pathGeometry } from '@/features/story-map/utils/pathGeometry'
import { useStoryArtifactNavigation } from '@/features/story-map/hooks/useStoryArtifactNavigation'
import type { LearningChapter } from '@/features/story-map/types'
import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { syncTierRunInCache } from '@/features/story-map/utils/tierRunCache'
import { useFocusTrap } from '@/shared/utils/useFocusTrap'

import { nextPlayableLevelId } from '@/features/story-map/utils/storyMapChapter'
import { StoryLevelTierPanel, StoryTrialsPanel } from './StoryAdventurePanels'
import { StoryChallengeNode, StoryPathLevelNode, type StoryTrialState } from './StoryPathNodes'

const PILL_CLOSE_MS = 180

// Callout geometry. The route's amplitude leaves the right side of the canvas
// permanently empty, which is where the level callout docks: beside-the-node
// placement cannot avoid covering a neighbour, because consecutive nodes sit
// one path step apart and the callout is taller than that step.
const CALLOUT_GAP = 16
const CALLOUT_EDGE = 10
const CALLOUT_MAX_WIDTH = 292
const CALLOUT_MIN_WIDTH = 208
const CALLOUT_CARET_INSET = 22
const DEFAULT_NODE_RADIUS = 37

export function StoryAdventurePath({
  chapter,
  levels,
  challenges,
  challengesLocked,
  loading,
  defaultTrialsOpen = false,
}: {
  chapter: LearningChapter
  levels: AdventureLevelSummary[]
  challenges: ChallengeSummary[]
  challengesLocked: boolean
  loading: boolean
  defaultTrialsOpen?: boolean
}) {
  const { openAdventureLevel, openChallengeArtifact } = useStoryArtifactNavigation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const startTierRunMutation = useMutation({
    mutationFn: ({ tierId, replay }: { tierId: number; replay?: boolean }) =>
      tierRunsApi.startRun(tierId, replay ? { replay: true } : undefined),
    onSuccess: (run) => {
      syncTierRunInCache(queryClient, run)
      navigate(`/adventure-tier-runs/${run.id}`)
    },
  })
  const currentLevelId = nextPlayableLevelId(levels, chapter.locked)
  const placeholderCount = Math.max(3, chapter.adventure_level_count || 6)
  const nodes: Array<AdventureLevelSummary | undefined> = levels.length
    ? levels
    : Array.from({ length: placeholderCount })
  const trials = allChallengeTrials(challenges)
  const [trialsOpen, setTrialsOpen] = useState(defaultTrialsOpen)
  const trialsPanelRef = useRef<HTMLElement | null>(null)
  const [selectedLevelId, setSelectedLevelId] = useState<number | null>(null)
  const [closingLevelId, setClosingLevelId] = useState<number | null>(null)
  const closeTimerRef = useRef<number | null>(null)

  const pathRef = useRef<HTMLDivElement | null>(null)
  const canvasRef = useRef<HTMLDivElement | null>(null)
  const [pathWidth, setPathWidth] = useState(640)
  // Ring size is breakpoint-dependent (it shrinks on small screens) and the
  // callout's gutter is measured from a node's outer edge, so read it off the
  // DOM rather than duplicating that media query as a constant here.
  const [nodeRadius, setNodeRadius] = useState(DEFAULT_NODE_RADIUS)

  const measureNodeRadius = useCallback(() => {
    const ring = canvasRef.current?.querySelector('.story-path-node-ring')
    const width = ring instanceof HTMLElement ? ring.offsetWidth : 0
    if (width > 0) setNodeRadius(width / 2)
  }, [])

  useEffect(() => {
    const el = pathRef.current
    if (!el) return
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width ?? 0
      if (width > 0) setPathWidth(Math.max(320, Math.min(720, Math.round(width))))
      measureNodeRadius()
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [measureNodeRadius])

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
    setTrialsOpen(defaultTrialsOpen)
    setSelectedLevelId(null)
    setClosingLevelId(null)
  }, [chapter.id, defaultTrialsOpen])

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

  useEffect(() => {
    if (!trialsOpen) return
    const frame = window.requestAnimationFrame(() => {
      trialsPanelRef.current?.scrollIntoView?.({ block: 'nearest' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [trialsOpen])

  // Traps focus inside the trials panel while open and restores it to
  // whatever opened it (the Challenge Gate node button) when it closes —
  // otherwise closing via Escape drops focus into the void, since the
  // focused trial card unmounts along with the rest of the panel.
  useFocusTrap(trialsPanelRef, trialsOpen)

  // One extra point: the chapter's challenge trials live on the same path,
  // as its final node.
  const { points, height } = useMemo(
    () => pathGeometry(nodes.length + 1, pathWidth),
    [nodes.length, pathWidth],
  )
  const routePathData = useMemo(() => pathDataFor(points), [points])
  const trialPoint = points[points.length - 1]

  const selectedTierNodeIndex = useMemo(
    () => nodes.findIndex((node) => node && node.id === selectedLevelId && node.tiers.length > 0),
    [nodes, selectedLevelId],
  )
  const selectedTierLevel =
    selectedTierNodeIndex >= 0 ? (nodes[selectedTierNodeIndex] as AdventureLevelSummary) : null
  const selectedTierPoint = selectedTierNodeIndex >= 0 ? points[selectedTierNodeIndex] : null
  const levelTierPanelRef = useRef<HTMLElement | null>(null)
  const [calloutHeight, setCalloutHeight] = useState(0)
  useFocusTrap(levelTierPanelRef, Boolean(selectedTierLevel))

  // Measured in a layout effect, so the callout is never painted at the
  // unmeasured (height 0) position first and then jumped into place.
  useLayoutEffect(() => {
    const el = levelTierPanelRef.current
    if (!el || !selectedTierLevel) {
      setCalloutHeight(0)
      return
    }
    const measure = () => setCalloutHeight(el.getBoundingClientRect().height)
    measure()
    if (typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(measure)
    observer.observe(el)
    return () => observer.disconnect()
  }, [selectedTierLevel])

  useLayoutEffect(() => {
    measureNodeRadius()
  }, [measureNodeRadius, nodes.length])

  // Escape leaves the callout. Without it the focus trap is inescapable from
  // the keyboard, since the only other way out is clicking the node again.
  useEffect(() => {
    if (!selectedTierLevel) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSelectedLevelId(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [selectedTierLevel])

  // A pointer press outside the callout dismisses it. The node that opened it
  // is excluded because it toggles on its own.
  useEffect(() => {
    if (!selectedTierLevel) return
    const onPointerDown = (event: PointerEvent) => {
      const target = event.target
      if (!(target instanceof Node)) return
      if (levelTierPanelRef.current?.contains(target)) return
      const selectedNode = canvasRef.current?.querySelector('.story-path-node[data-selected]')
      if (selectedNode?.contains(target)) return
      setSelectedLevelId(null)
    }
    window.addEventListener('pointerdown', onPointerDown)
    return () => window.removeEventListener('pointerdown', onPointerDown)
  }, [selectedTierLevel])

  const trialsCleared = trials.length > 0 && trials.every((trial) => trial.completion)
  const clearedTrialCount = trials.filter((trial) => trial.completion).length
  const trialState: StoryTrialState = loading
    ? 'loading'
    : challengesLocked || !trials.length
    ? 'locked'
    : trialsCleared
    ? 'cleared'
    : 'ready'
  const trialDisabled = trialState === 'locked' || trialState === 'loading'

  // The gutter the callout docks into, derived from the route's own widest
  // node rather than a guessed constant, so it tracks any change to the path
  // geometry or to the ring size at a breakpoint.
  const calloutRail = useMemo(() => {
    const widestNodeX = points.reduce((max, point) => Math.max(max, point.x), 0)
    const left = Math.round(widestNodeX + nodeRadius + CALLOUT_GAP)
    const width = Math.min(CALLOUT_MAX_WIDTH, pathWidth - left)
    return { left, width, docked: width >= CALLOUT_MIN_WIDTH }
  }, [points, nodeRadius, pathWidth])

  // Vertically centred on its node, clamped inside the canvas. The leader is
  // drawn to wherever the callout actually lands, so a clamped one still
  // reads as belonging to the node that opened it.
  const calloutPlacement = useMemo(() => {
    if (!selectedTierPoint || !calloutRail.docked) return null
    const maxTop = Math.max(height - calloutHeight - CALLOUT_EDGE, CALLOUT_EDGE)
    const top = Math.round(
      Math.min(Math.max(selectedTierPoint.y - calloutHeight / 2, CALLOUT_EDGE), maxTop),
    )
    const caretY = Math.min(
      Math.max(selectedTierPoint.y - top, CALLOUT_CARET_INSET),
      Math.max(calloutHeight - CALLOUT_CARET_INSET, CALLOUT_CARET_INSET),
    )
    const startX = selectedTierPoint.x + nodeRadius - 1
    const startY = selectedTierPoint.y
    const endX = calloutRail.left - 4
    const endY = top + caretY
    const bend = Math.max((endX - startX) * 0.45, 18)
    const leader = [
      `M${startX} ${startY}`,
      `C${startX + bend} ${startY} ${endX - bend} ${endY} ${endX} ${endY}`,
    ].join(' ')
    return {
      top,
      leader,
      leaderLength: Math.round(Math.hypot(endX - startX, endY - startY) * 1.2 + 32),
      endX,
      endY,
    }
  }, [selectedTierPoint, calloutRail, calloutHeight, height, nodeRadius])

  // Inline placement puts the callout below the whole path, which can be far
  // from the node that was tapped - bring it into view the way the Challenge
  // Gate panel does.
  useEffect(() => {
    if (!selectedTierLevel || calloutRail.docked) return
    const frame = window.requestAnimationFrame(() => {
      levelTierPanelRef.current?.scrollIntoView?.({ block: 'nearest' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [selectedTierLevel, calloutRail.docked])

  const levelTierPanelStyle: React.CSSProperties | undefined = calloutPlacement
    ? ({
        '--callout-left': `${calloutRail.left}px`,
        '--callout-top': `${calloutPlacement.top}px`,
        '--callout-width': `${calloutRail.width}px`,
      } as React.CSSProperties)
    : undefined

  return (
    <div className="story-adventure-path" ref={pathRef}>
      <div className="story-path-canvas" ref={canvasRef} style={{ width: pathWidth, height }}>
        <svg
          className="story-route-line"
          viewBox={`0 0 ${pathWidth} ${height}`}
          width={pathWidth}
          height={height}
          aria-hidden="true"
          focusable="false"
        >
          <path d={routePathData} />
        </svg>

        {nodes.map((level, index) => (
          <StoryPathLevelNode
            key={level?.id ?? `placeholder-${index}`}
            level={level}
            index={index}
            position={points[index]}
            chapterLocked={chapter.locked}
            currentLevelId={currentLevelId}
            loading={loading}
            selectedLevelId={selectedLevelId}
            closingLevelId={closingLevelId}
            onToggle={toggleLevelPill}
            onOpenLevel={openAdventureLevel}
          />
        ))}

        <StoryChallengeNode
          trialCount={trials.length}
          state={trialState}
          open={trialsOpen}
          disabled={trialDisabled}
          position={trialPoint}
          loading={loading}
          chapterLocked={chapter.locked}
          chapterLockReason={chapter.lock_reason}
          onToggle={() => setTrialsOpen((open) => !open)}
        />

        {selectedTierLevel && calloutPlacement ? (
          <svg
            className="story-callout-leader"
            viewBox={`0 0 ${pathWidth} ${height}`}
            width={pathWidth}
            height={height}
            aria-hidden="true"
            focusable="false"
          >
            <path
              d={calloutPlacement.leader}
              style={{ '--leader-length': calloutPlacement.leaderLength } as React.CSSProperties}
            />
            <circle cx={calloutPlacement.endX} cy={calloutPlacement.endY} r={2.6} />
          </svg>
        ) : null}

        {selectedTierLevel && calloutPlacement ? (
          <StoryLevelTierPanel
            level={selectedTierLevel}
            levelNumber={selectedTierNodeIndex + 1}
            panelRef={levelTierPanelRef}
            placement="docked"
            style={levelTierPanelStyle}
            pendingTierId={startTierRunMutation.variables?.tierId}
            isStarting={startTierRunMutation.isPending}
            onClose={() => setSelectedLevelId(null)}
            onStartTier={(tierId, replay) => startTierRunMutation.mutate({ tierId, replay })}
            onOpenDrill={() => navigate(`/adventure-levels/${selectedTierLevel.id}/drill`)}
          />
        ) : null}
      </div>

      {selectedTierLevel && !calloutPlacement ? (
        <StoryLevelTierPanel
          level={selectedTierLevel}
          levelNumber={selectedTierNodeIndex + 1}
          panelRef={levelTierPanelRef}
          placement="inline"
          pendingTierId={startTierRunMutation.variables?.tierId}
          isStarting={startTierRunMutation.isPending}
          onClose={() => setSelectedLevelId(null)}
          onStartTier={(tierId, replay) => startTierRunMutation.mutate({ tierId, replay })}
          onOpenDrill={() => navigate(`/adventure-levels/${selectedTierLevel.id}/drill`)}
        />
      ) : null}

      {trialsOpen ? (
        <StoryTrialsPanel
          challenges={challenges}
          challengesLocked={challengesLocked}
          clearedTrialCount={clearedTrialCount}
          loading={loading}
          panelRef={trialsPanelRef}
          trialCount={trials.length}
          onOpenTrial={openChallengeArtifact}
        />
      ) : null}
    </div>
  )
}
