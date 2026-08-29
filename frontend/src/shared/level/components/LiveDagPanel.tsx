import { memo, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import ReactFlow, { Background, Controls, ReactFlowProvider } from 'reactflow'

import type { RepositorySnapshot } from '@/shared/level/types'
import { Card, CardContent, CardHeader } from '@/shared/components/Card'
import { graphLayoutSignature } from '@/shared/level/utils/graphLayoutSignature'
import { writePreference } from '@/shared/utils/persistentState'
import { cn } from '@/shared/utils/cn'

import { MAX_DAG_ZOOM, MIN_DAG_ZOOM, NO_DELTA, VARIANT_COLORS } from './live-dag/constants'
import { FitViewOnTopologyChange } from './live-dag/FitViewOnTopologyChange'
import { buildGraph, layoutPositionsCache, normalizeSnapshot, rememberLayoutPositions, snapshotDelta } from './live-dag/graph'
import { CommitDetailsPanel, CommitNode, EmptyRepositoryNode, RepositoryDetails } from './live-dag/nodes'
import type { CommitNodeData, DagActivity, DagLayoutDirection, DagVariant, EnteringDelta } from './live-dag/types'

const commitNodeTypes = {
  commit: memo(CommitNode),
  emptyRepository: memo(EmptyRepositoryNode),
}

function handleReactFlowError(code: string, message: string) {
  if (code === '002') return
  console.warn(message)
}

export function LiveDagPanel({
  title = 'Live DAG',
  snapshot,
  className,
  contentClassName,
  showRepositoryDetails = false,
  fitViewPadding = 0.08,
  zoomStorageKey,
  animateChanges = false,
  pauseChangeAnimations = false,
  activity = 'idle',
  layoutDirection = 'vertical',
}: {
  title?: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  /**
   * When set, the learner's manual zoom is remembered under this key and kept
   * across topology changes (auto-fit re-centers but no longer overrides zoom).
   */
  zoomStorageKey?: string
  /** Animate per-command deltas: new commits pop in, new edges draw in, moved
   *  ref pills slide up. Off for static diagrams (Target DAG). */
  animateChanges?: boolean
  /** Keep newly rendered graph deltas at their first frame until a command resolves. */
  pauseChangeAnimations?: boolean
  /** Concise state signal used by puzzle-style DAG consumers. */
  activity?: DagActivity
  /** Controls whether commits flow top-to-bottom or left-to-right. */
  layoutDirection?: DagLayoutDirection
}) {
  return (
    <RepositoryStateDiagram
      title={title}
      snapshot={snapshot}
      className={className}
      contentClassName={contentClassName}
      showRepositoryDetails={showRepositoryDetails}
      fitViewPadding={fitViewPadding}
      zoomStorageKey={zoomStorageKey}
      animateChanges={animateChanges}
      pauseChangeAnimations={pauseChangeAnimations}
      activity={activity}
      layoutDirection={layoutDirection}
    />
  )
}

const RepositoryStateDiagramBody = memo(function RepositoryStateDiagramBody({
  title,
  snapshot,
  className,
  contentClassName,
  showRepositoryDetails = false,
  fitViewPadding = 0.08,
  variant = 'cyan',
  zoomStorageKey,
  animateChanges = false,
  pauseChangeAnimations = false,
  activity = 'idle',
  layoutDirection = 'vertical',
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
  zoomStorageKey?: string
  animateChanges?: boolean
  pauseChangeAnimations?: boolean
  activity?: DagActivity
  layoutDirection?: DagLayoutDirection
}) {
  const colors = VARIANT_COLORS[variant]
  const normalizedSnapshot = useMemo(() => normalizeSnapshot(snapshot), [snapshot])
  const layoutSignature = useMemo(() => graphLayoutSignature(normalizedSnapshot), [normalizedSnapshot])
  const layoutCacheKey = `${layoutDirection}:${layoutSignature}`

  // Per-command enter animations: diff the snapshot against the previous one
  // (in an effect, so render never touches refs), hold the delta long enough
  // for the CSS animations to finish, then clear.
  const [entering, setEntering] = useState<EnteringDelta>(NO_DELTA)
  const previousSnapshotRef = useRef<RepositorySnapshot | null>(null)
  useLayoutEffect(() => {
    const previous = previousSnapshotRef.current
    previousSnapshotRef.current = normalizedSnapshot
    if (!animateChanges || !previous || previous === normalizedSnapshot) return
    const delta = snapshotDelta(previous, normalizedSnapshot)
    if (delta === NO_DELTA) {
      setEntering(NO_DELTA)
      return
    }
    setEntering(delta)
  }, [animateChanges, normalizedSnapshot])

  useEffect(() => {
    const hasDelta = entering.commits.size > 0 || entering.refsByCommit.size > 0 || Boolean(entering.headTarget)
    if (!hasDelta || pauseChangeAnimations) return
    const timer = window.setTimeout(() => setEntering(NO_DELTA), 760)
    return () => window.clearTimeout(timer)
  }, [entering, pauseChangeAnimations])

  const { nodes, edges } = useMemo(() => {
    const cached = layoutPositionsCache.get(layoutCacheKey)
    const graph = buildGraph(normalizedSnapshot, variant, layoutDirection, cached)
    if (!cached) {
      rememberLayoutPositions(
        layoutCacheKey,
        new Map(graph.nodes.map((node) => [node.id, node.position])),
      )
    }
    return graph
  }, [normalizedSnapshot, variant, layoutCacheKey, layoutDirection])
  const nodeTypes = useMemo(() => commitNodeTypes, [])
  const [activeCommitId, setActiveCommitId] = useState<string | null>(null)
  const dismissCommit = useCallback((commitId: string) => {
    setActiveCommitId((currentId) => (currentId === commitId ? null : currentId))
  }, [])
  const diagramNodes = useMemo(
    () =>
      nodes.map((node) => {
        if (node.type !== 'commit') return node
        const commitId = node.id
        return {
          ...node,
          data: {
            ...(node.data as CommitNodeData),
            isActive: activeCommitId === commitId,
            isEntering: entering.commits.has(commitId),
            enteringRefs: entering.refsByCommit.get(commitId),
            enteringHead: entering.headTarget === commitId,
            onActivate: () => setActiveCommitId(commitId),
            onDismiss: () => dismissCommit(commitId),
          },
        }
      }),
    [activeCommitId, dismissCommit, entering, nodes],
  )
  const diagramEdges = useMemo(
    () =>
      entering.commits.size
        ? edges.map((edge) =>
            entering.commits.has(edge.target) ? { ...edge, className: 'dag-edge-enter' } : edge,
          )
        : edges,
    [edges, entering],
  )
  const activeCommitData = useMemo(() => {
    const activeNode = diagramNodes.find((node) => node.type === 'commit' && node.id === activeCommitId)
    return activeNode?.data as CommitNodeData | undefined
  }, [activeCommitId, diagramNodes])

  return (
    <Card
      className={cn(
        'live-dag-panel min-h-0 overflow-hidden shadow-none',
        pauseChangeAnimations && 'is-change-paused',
        activity === 'processing' && 'is-processing',
        className,
      )}
      style={{ borderTop: `1.5px solid ${colors.border}` }}
    >
      <CardHeader className="p-3" style={{ background: colors.headerBg }}>
        <span className={cn('panel-eyebrow', colors.titleClass)}>{title}</span>
        {activity !== 'idle' ? (
          <span className="sr-only" role="status" aria-live="polite">
            {activityLabel(activity)}
          </span>
        ) : null}
      </CardHeader>
      <CardContent className={cn('p-0', contentClassName)}>
        <div className="relative h-full min-h-0">
          <div
            className="pointer-events-none absolute inset-0 z-0"
            style={{
              background: colors.gradientBg,
            }}
          />
          <ReactFlow
            className="h-full w-full"
            style={{ height: '100%', width: '100%', background: 'transparent' }}
            nodes={diagramNodes}
            edges={diagramEdges}
            nodesDraggable={false}
            nodesConnectable={false}
            nodeTypes={nodeTypes}
            panOnScroll
            minZoom={MIN_DAG_ZOOM}
            maxZoom={MAX_DAG_ZOOM}
            proOptions={{ hideAttribution: true }}
            onError={handleReactFlowError}
            onMoveEnd={
              zoomStorageKey
                ? (event, viewport) => {
                    // Responsive/topology fitView calls have no source event;
                    // persisting them would make a phone-sized zoom leak into
                    // the next desktop session. Store only learner gestures.
                    if (event) writePreference(zoomStorageKey, viewport.zoom)
                  }
                : undefined
            }
          >
            <Background gap={18} color="hsl(var(--foreground) / 0.05)" />
            <Controls
              className="dag-controls"
              position="bottom-right"
              showInteractive={false}
              aria-label={`${title} view controls`}
            />
            <FitViewOnTopologyChange
              fitSignature={layoutCacheKey}
              topologySignature={layoutSignature}
              fitViewPadding={fitViewPadding}
              zoomStorageKey={zoomStorageKey}
            />
          </ReactFlow>
          <CommitDetailsPanel data={activeCommitData ?? null} />
        </div>
        {showRepositoryDetails ? <RepositoryDetails snapshot={normalizedSnapshot} /> : null}
      </CardContent>
    </Card>
  )
})

function RepositoryStateDiagram({
  title,
  snapshot,
  className,
  contentClassName,
  showRepositoryDetails = false,
  fitViewPadding = 0.08,
  variant = 'cyan',
  zoomStorageKey,
  animateChanges = false,
  pauseChangeAnimations = false,
  activity = 'idle',
  layoutDirection = 'vertical',
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
  zoomStorageKey?: string
  animateChanges?: boolean
  pauseChangeAnimations?: boolean
  activity?: DagActivity
  layoutDirection?: DagLayoutDirection
}) {
  return (
    <ReactFlowProvider>
      <RepositoryStateDiagramBody
        title={title}
        snapshot={snapshot}
        className={className}
        contentClassName={contentClassName}
        showRepositoryDetails={showRepositoryDetails}
        fitViewPadding={fitViewPadding}
        variant={variant}
        zoomStorageKey={zoomStorageKey}
        animateChanges={animateChanges}
        pauseChangeAnimations={pauseChangeAnimations}
        activity={activity}
        layoutDirection={layoutDirection}
      />
    </ReactFlowProvider>
  )
}

function activityLabel(activity: DagActivity) {
  switch (activity) {
    case 'processing': return 'Repository command running'
    case 'updated': return 'Repository updated'
    case 'unchanged': return 'Repository unchanged'
    case 'solved': return 'Repository puzzle solved'
    case 'error': return 'Repository command failed'
    default: return 'Repository ready'
  }
}
