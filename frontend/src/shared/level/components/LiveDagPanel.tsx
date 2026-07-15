import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
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
import type { CommitNodeData, DagLayoutDirection, DagVariant, EnteringDelta } from './live-dag/types'

const commitNodeTypes = {
  commit: memo(CommitNode),
  emptyRepository: memo(EmptyRepositoryNode),
}

function handleReactFlowError(code: string, message: string) {
  if (code === '002') return
  console.warn(message)
}

export type DagBadge = 'live' | 'target'

export function LiveDagPanel({
  title = 'Live DAG',
  snapshot,
  className,
  contentClassName,
  showRepositoryDetails = false,
  fitViewPadding = 0.08,
  zoomStorageKey,
  animateChanges = false,
  layoutDirection = 'vertical',
  badge,
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
  /** Controls whether commits flow top-to-bottom or left-to-right. */
  layoutDirection?: DagLayoutDirection
  /** Header tag: `live` = pulsing live dot, `target` = amber expected-state chip. */
  badge?: DagBadge
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
      layoutDirection={layoutDirection}
      badge={badge}
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
  layoutDirection = 'vertical',
  badge,
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
  layoutDirection?: DagLayoutDirection
  badge?: DagBadge
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
  useEffect(() => {
    const previous = previousSnapshotRef.current
    previousSnapshotRef.current = normalizedSnapshot
    if (!animateChanges || !previous || previous === normalizedSnapshot) return
    const delta = snapshotDelta(previous, normalizedSnapshot)
    if (delta === NO_DELTA) return
    setEntering(delta)
    const timer = window.setTimeout(() => setEntering(NO_DELTA), 700)
    return () => window.clearTimeout(timer)
  }, [animateChanges, normalizedSnapshot])

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
      className={cn('min-h-0 overflow-hidden shadow-none', className)}
      style={{ borderTop: `1.5px solid ${colors.border}` }}
    >
      <CardHeader className="p-3" style={{ background: colors.headerBg }}>
        <div className="flex items-center gap-2">
          <span className={cn('panel-eyebrow', colors.titleClass)}>{title}</span>
          {badge === 'live' ? (
            <span className="dag-badge dag-badge--live ml-auto">
              <span className="dag-badge-dot" aria-hidden="true" />
              Live
            </span>
          ) : null}
          {badge === 'target' ? <span className="dag-badge dag-badge--target ml-auto">Expected State</span> : null}
        </div>
      </CardHeader>
      <CardContent className={cn('p-0', contentClassName)}>
        <div className="relative h-full min-h-0">
          <div
            className="pointer-events-none absolute inset-0 z-0"
            style={{
              background: colors.gradientBg,
              animation: 'bg-drift 20s ease-in-out infinite alternate',
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
            onlyRenderVisibleElements
            minZoom={MIN_DAG_ZOOM}
            maxZoom={MAX_DAG_ZOOM}
            proOptions={{ hideAttribution: true }}
            onError={handleReactFlowError}
            onMoveEnd={
              zoomStorageKey
                ? (_event, viewport) => writePreference(zoomStorageKey, viewport.zoom)
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
              layoutSignature={layoutCacheKey}
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

export function RepositoryStateDiagram({
  title,
  snapshot,
  className,
  contentClassName,
  showRepositoryDetails = false,
  fitViewPadding = 0.08,
  variant = 'cyan',
  zoomStorageKey,
  animateChanges = false,
  layoutDirection = 'vertical',
  badge,
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
  layoutDirection?: DagLayoutDirection
  badge?: DagBadge
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
        layoutDirection={layoutDirection}
        badge={badge}
      />
    </ReactFlowProvider>
  )
}
