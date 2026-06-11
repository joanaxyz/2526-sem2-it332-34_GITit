import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import ReactFlow, { Background, Handle, Position, ReactFlowProvider, useReactFlow } from 'reactflow'
import type { Edge, Node, NodeProps } from 'reactflow'

import type { RepositoryCommit, RepositorySnapshot, RepositoryValue } from '@/shared/practice/types'
import { Card, CardContent, CardHeader } from '@/shared/components/Card'
import { graphLayoutSignature } from '@/shared/practice/utils/graphLayoutSignature'
import { readPreference, writePreference } from '@/shared/utils/persistentState'
import { cn } from '@/shared/utils/cn'

const MIN_DAG_ZOOM = 0.55
const MAX_DAG_ZOOM = 1.6

type DagVariant = 'cyan'

type RefKind = 'local' | 'remote'

type RefLabel = {
  name: string
  kind: RefKind
}

type CommitNodeData = {
  commit: RepositoryCommit
  refs: RefLabel[]
  activeRef: string | null
  isHead: boolean
  isDetachedHead: boolean
  variant: DagVariant
  isActive?: boolean
  onActivate?: () => void
  onDismiss?: () => void
}

type EmptyRepositoryNodeData = {
  branchName: string
  variant: DagVariant
}

const VARIANT_COLORS = {
  cyan: {
    border: 'rgba(0,245,212,0.42)',
    headerBg: 'rgba(0,245,212,0.025)',
    iconShadow: 'drop-shadow(0 0 4px rgba(0,245,212,0.55))',
    titleClass: 'text-primary',
    gradientBg: 'radial-gradient(ellipse at 30% 40%, rgba(0,245,212,0.05) 0%, transparent 62%)',
    dotColor: 'rgba(0,245,212,0.06)',
    headNode: 'border-2 border-primary bg-primary/15 text-primary dag-head-glow',
    activePill: 'border-primary/55 bg-primary/10 text-primary shadow-[0_0_8px_rgba(0,245,212,0.22)]',
    emptyHead: 'dag-head-glow border-2 border-dashed border-primary bg-primary/10 text-primary',
    emptyPill: 'border-primary/50 bg-primary/10 text-primary shadow-[0_0_6px_rgba(0,245,212,0.2)]',
  },
} as const

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
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
  zoomStorageKey?: string
}) {
  const colors = VARIANT_COLORS[variant]
  const normalizedSnapshot = useMemo(() => normalizeSnapshot(snapshot), [snapshot])
  const layoutSignature = useMemo(() => graphLayoutSignature(normalizedSnapshot), [normalizedSnapshot])
  const { nodes, edges } = useMemo(() => {
    const cached = layoutPositionsCache.get(layoutSignature)
    const graph = buildGraph(normalizedSnapshot, variant, cached)
    if (!cached) {
      rememberLayoutPositions(
        layoutSignature,
        new Map(graph.nodes.map((node) => [node.id, node.position])),
      )
    }
    return graph
  }, [normalizedSnapshot, variant, layoutSignature])
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
            onActivate: () => setActiveCommitId(commitId),
            onDismiss: () => dismissCommit(commitId),
          },
        }
      }),
    [activeCommitId, dismissCommit, nodes],
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
          <GitCommitHorizontal
            className="size-4"
            style={{ filter: colors.iconShadow }}
          />
          <span className={cn('text-sm font-bold tracking-wide', colors.titleClass)}>{title}</span>
          {normalizedSnapshot.commits.length > 0 && (
            <span className="ml-auto font-mono text-[10px] font-medium text-muted-foreground/60">
              {normalizedSnapshot.commits.length} commit{normalizedSnapshot.commits.length === 1 ? '' : 's'}
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent
        className={cn(
          showRepositoryDetails ? 'grid h-[21rem] grid-rows-[minmax(0,1fr)_auto] p-0' : 'h-[21rem] p-0',
          contentClassName,
        )}
      >
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
            edges={edges}
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
            <Background gap={18} color="rgba(255,255,255,0.05)" />
            <FitViewOnTopologyChange
              layoutSignature={layoutSignature}
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
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
  zoomStorageKey?: string
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
      />
    </ReactFlowProvider>
  )
}

function FitViewOnTopologyChange({
  layoutSignature,
  fitViewPadding,
  zoomStorageKey,
}: {
  layoutSignature: string
  fitViewPadding: number
  zoomStorageKey?: string
}) {
  const { fitView } = useReactFlow()
  const previousSignature = useRef<string | null>(null)

  useEffect(() => {
    if (previousSignature.current === layoutSignature) return
    previousSignature.current = layoutSignature
    const frameId = window.requestAnimationFrame(() => {
      // Pinning fitView's min/max zoom to the saved level makes it re-center the
      // graph at the learner's chosen zoom instead of refitting to the contents.
      const savedZoom = zoomStorageKey ? readPreference<number | null>(zoomStorageKey, null) : null
      if (savedZoom != null && Number.isFinite(savedZoom)) {
        const zoom = Math.min(Math.max(savedZoom, MIN_DAG_ZOOM), MAX_DAG_ZOOM)
        void fitView({ padding: fitViewPadding, duration: 0, minZoom: zoom, maxZoom: zoom })
      } else {
        void fitView({ padding: fitViewPadding, duration: 0 })
      }
    })
    return () => window.cancelAnimationFrame(frameId)
  }, [fitView, fitViewPadding, layoutSignature, zoomStorageKey])

  return null
}

function CommitNode({ data }: NodeProps<CommitNodeData>) {
  const colors = VARIANT_COLORS[data.variant]
  const visibleRefs = orderRefs(data.refs, data.activeRef).slice(0, 4)
  const hiddenRefCount = Math.max(data.refs.length - visibleRefs.length, 0)
  const label = [
    `Commit ${data.commit.id}`,
    data.commit.message ? `message ${data.commit.message}` : null,
    data.refs.length ? `refs ${data.refs.map((ref) => ref.name).join(', ')}` : null,
    data.isHead ? 'HEAD points here' : null,
  ]
    .filter(Boolean)
    .join(', ')

  return (
    <div
      className="relative z-10 flex w-36 flex-col items-center gap-2"
      onMouseEnter={data.onActivate}
      onMouseLeave={data.onDismiss}
      onFocus={data.onActivate}
      onBlur={(event) => {
        const nextFocusTarget = event.relatedTarget
        if (!(nextFocusTarget instanceof HTMLElement) || !event.currentTarget.contains(nextFocusTarget)) {
          data.onDismiss?.()
        }
      }}
    >
      <Handle className="opacity-0" type="target" position={Position.Top} />
      <button
        type="button"
        aria-label={label}
        title={label}
        onClick={data.onActivate}
        className={cn(
          'grid size-16 place-items-center rounded-full font-mono text-sm font-semibold outline-none transition-all focus-visible:ring-2 focus-visible:ring-ring',
          data.isHead
            ? colors.headNode
            : 'border border-border bg-card text-foreground shadow-sm',
          data.isActive && 'ring-2 ring-primary/70 ring-offset-2 ring-offset-background',
        )}
      >
        {shortenHash(data.commit.id)}
      </button>
      {(visibleRefs.length > 0 || data.isDetachedHead) && (
        <div className="flex max-w-36 flex-wrap justify-center gap-1">
          {data.isDetachedHead && (
            <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-0.5 text-[10px] font-semibold leading-none text-accent">
              HEAD
            </span>
          )}
          {visibleRefs.map((ref) => {
            const isActive = ref.name === data.activeRef
            return (
              <span
                className={cn(
                  'max-w-32 truncate rounded-full border px-2 py-0.5 text-[10px] font-semibold leading-none',
                  isActive
                    ? colors.activePill
                    : ref.kind === 'remote'
                      ? 'border-sky-500/35 bg-sky-500/10 text-sky-700 dark:text-sky-300'
                      : 'border-border bg-secondary text-muted-foreground',
                )}
                key={`${ref.kind}:${ref.name}`}
                title={ref.name}
              >
                {ref.name}
              </span>
            )
          })}
          {hiddenRefCount > 0 && (
            <span className="rounded-full border border-border bg-secondary px-2 py-0.5 text-[10px] font-medium leading-none text-muted-foreground">
              +{hiddenRefCount}
            </span>
          )}
        </div>
      )}
      <Handle className="opacity-0" type="source" position={Position.Bottom} />
    </div>
  )
}

function CommitDetailsPanel({ data }: { data: CommitNodeData | null }) {
  if (!data) return null

  const isMerge = data.commit.is_merge || data.commit.parents.length > 1

  return (
    <div
      className="pointer-events-none absolute right-3 top-3 z-50 w-60 max-w-[calc(100%-1.5rem)] overflow-hidden rounded-md border border-border/80 bg-card/90 p-3 text-left text-xs shadow-2xl shadow-black/25 backdrop-blur-md"
      data-testid="commit-details-overlay"
      role="tooltip"
    >
      <div className="flex items-center justify-between gap-2">
        <p className="font-mono text-[11px] font-semibold text-foreground">{shortenHash(data.commit.id)}</p>
        {data.isHead ? (
          <span className="shrink-0 rounded-full border border-accent/45 bg-accent/15 px-2 py-0.5 text-[10px] font-semibold leading-none text-accent">
            HEAD
          </span>
        ) : null}
      </div>
      <p className="mt-1.5 line-clamp-2 font-medium text-foreground" title={data.commit.message || '(empty)'}>
        Message: {data.commit.message || '(empty)'}
      </p>
      {data.refs.length || isMerge ? (
        <div className="mt-2 flex flex-wrap gap-1">
          {isMerge ? (
            <span className="rounded-full border border-accent/35 bg-accent/10 px-2 py-0.5 text-[10px] font-medium leading-none text-accent">
              merge
            </span>
          ) : null}
          {data.refs.map((ref) => (
            <span
              key={`${ref.kind}:${ref.name}`}
              className="max-w-[10rem] truncate rounded-full border border-border bg-secondary px-2 py-0.5 text-[10px] font-medium leading-none text-muted-foreground"
              title={ref.name}
            >
              {ref.name}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function EmptyRepositoryNode({ data }: NodeProps<EmptyRepositoryNodeData>) {
  const colors = VARIANT_COLORS[data.variant]
  return (
    <div className="flex w-32 flex-col items-center gap-2">
      <div className={cn('grid size-16 place-items-center rounded-full font-mono text-xs font-semibold', colors.emptyHead)}>
        HEAD
      </div>
      <span className={cn('max-w-28 truncate rounded-full border px-2 py-0.5 text-[10px] font-semibold leading-none', colors.emptyPill)}>
        {data.branchName}
      </span>
      <div className="mt-0.5 rounded border border-dashed border-muted-foreground/20 px-2.5 py-1.5 text-center">
        <span className="text-[10px] font-medium leading-none text-muted-foreground/55">No commits yet</span>
      </div>
    </div>
  )
}

function RepositoryDetails({ snapshot }: { snapshot: RepositorySnapshot }) {
  const staged = Object.entries(snapshot.staging).map(([path, value]) => `${path}${formatTokens(value)}`)
  const working = Object.entries(snapshot.working_tree).map(([path, value]) => `${path}${formatTokens(value)}`)
  const ignored = Object.entries(snapshot.working_tree)
    .filter(([, value]) => entryStatus(value) === 'ignored')
    .map(([path]) => path)
  const conflicts = snapshot.conflicts
  const remotes = Object.entries(snapshot.remotes ?? {})
  const remoteBranches = Object.entries(snapshot.remote_branches ?? {})
  const upstream = Object.entries(snapshot.upstream_tracking ?? {})
  const stashCount = snapshot.stash_stack?.length ?? 0
  const metadata = Object.entries(snapshot.operation_metadata ?? {}).map(([key, value]) => `${key}: ${formatValue(value)}`)
  const partialHunks = Object.entries(snapshot.partial_hunks ?? {}).map(([path, value]) => `${path}${formatTokens(value as RepositoryValue)}`)

  return (
    <div className="max-h-28 overflow-auto border-t border-border bg-background/95 px-3 py-2 text-[11px]">
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        <SummaryLine label="Staged" value={formatPaths(staged)} />
        <SummaryLine label="Working tree" value={formatPaths(working)} />
        <SummaryLine label="Ignored" value={formatPaths(ignored)} />
        <SummaryLine label="Conflicts" value={formatPaths(conflicts)} />
        <SummaryLine
          label="Remotes"
          value={remotes.length ? remotes.map(([name, url]) => `${name} -> ${url}`).join(', ') : 'none'}
        />
        <SummaryLine
          label="Remote branches"
          value={
            remoteBranches.length
              ? remoteBranches.map(([name, target]) => `${name} -> ${target ?? '(none)'}`).join(', ')
              : 'none'
          }
        />
        <SummaryLine
          label="Upstream"
          value={upstream.length ? upstream.map(([name, target]) => `${name} -> ${target}`).join(', ') : 'none'}
        />
        <SummaryLine label="Stash" value={stashCount ? `${stashCount} entr${stashCount === 1 ? 'y' : 'ies'}` : 'none'} />
        <SummaryLine label="Hunks" value={formatPaths(partialHunks)} />
        <SummaryLine label="Metadata" value={formatPaths(metadata)} />
      </div>
    </div>
  )
}

function SummaryLine({ label, value }: { label: string; value: string }) {
  return (
    <p className="min-w-0 truncate text-muted-foreground" title={`${label}: ${value}`}>
      <span className="font-semibold text-foreground">{label}:</span> {value}
    </p>
  )
}

// dagre layout is the heaviest per-command cost, but node positions depend only
// on commit topology (exactly what graphLayoutSignature captures). Cache positions
// per topology so ref/HEAD/staging-only commands (git add, branch, switch, status…)
// refresh the cheap node data without re-running a full graph layout. Module level
// so the cache is shared across diagram instances (live + expected often match)
// and stays out of render-time ref/state mutation territory.
const layoutPositionsCache = new Map<string, Map<string, { x: number; y: number }>>()
const LAYOUT_CACHE_MAX_ENTRIES = 64

function rememberLayoutPositions(
  signature: string,
  positions: Map<string, { x: number; y: number }>,
) {
  layoutPositionsCache.set(signature, positions)
  while (layoutPositionsCache.size > LAYOUT_CACHE_MAX_ENTRIES) {
    const oldest = layoutPositionsCache.keys().next().value
    if (oldest === undefined) break
    layoutPositionsCache.delete(oldest)
  }
}

function buildGraph(
  snapshot: RepositorySnapshot,
  variant: DagVariant,
  cachedPositions?: Map<string, { x: number; y: number }>,
): { nodes: Node[]; edges: Edge[] } {
  const graph = new dagre.graphlib.Graph()
  graph.setDefaultEdgeLabel(() => ({}))
  graph.setGraph({ rankdir: 'TB', nodesep: 56, ranksep: 88 })

  if (!snapshot.commits.length) {
    const branchName =
      snapshot.head.type === 'branch' && snapshot.head.name
        ? snapshot.head.name
        : (Object.entries(snapshot.branches)
            .filter(([, target]) => target === null)
            .map(([name]) => name)
            .sort()[0] ?? 'unborn branch')
    graph.setNode('__empty__', { width: 128, height: 104 })
    dagre.layout(graph)
    const point = graph.node('__empty__')

    return {
      nodes: [
        {
          id: '__empty__',
          type: 'emptyRepository',
          position: { x: point.x - 64, y: point.y - 52 },
          data: { branchName, variant },
        },
      ],
      edges: [],
    }
  }

  const headTarget = snapshot.head.target ?? headTargetFromBranches(snapshot)
  const nodeSizes = new Map<string, { width: number; height: number }>()
  const nodes: Node<CommitNodeData>[] = snapshot.commits.map((commit) => {
    const refs = refsForCommit(snapshot, commit.id)
    const isHead = headTarget === commit.id
    const activeRef = snapshot.head.type === 'branch' && isHead ? (snapshot.head.name ?? null) : null
    const size = { width: 144, height: refs.length || (isHead && snapshot.head.type === 'detached') ? 108 : 76 }
    nodeSizes.set(commit.id, size)
    graph.setNode(commit.id, size)

    return {
      id: commit.id,
      type: 'commit',
      position: { x: 0, y: 0 },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        commit,
        refs,
        activeRef,
        isHead,
        isDetachedHead: isHead && snapshot.head.type === 'detached',
        variant,
      },
    }
  })

  const edges: Edge[] = []
  for (const commit of snapshot.commits) {
    for (const parent of commit.parents ?? []) {
      edges.push({
        id: `${parent}-${commit.id}`,
        source: parent,
        target: commit.id,
        type: 'smoothstep',
        style: { stroke: 'hsl(var(--muted-foreground))', strokeWidth: 1.4 },
      })
      graph.setEdge(parent, commit.id)
    }
  }

  if (!cachedPositions) {
    dagre.layout(graph)
  }
  return {
    nodes: nodes.map((node) => {
      const cachedPosition = cachedPositions?.get(node.id)
      if (cachedPosition) return { ...node, position: cachedPosition }
      const point = graph.node(node.id)
      const size = nodeSizes.get(node.id) ?? { width: 144, height: 76 }
      return { ...node, position: { x: point.x - size.width / 2, y: point.y - size.height / 2 } }
    }),
    edges,
  }
}

function normalizeSnapshot(snapshot: RepositorySnapshot): RepositorySnapshot {
  const branches = snapshot.branches ?? {}
  const head = { ...snapshot.head }
  if (head.type === 'branch' && head.target === undefined) {
    head.target = branches[head.name ?? ''] ?? null
  }
  return {
    repository_initialized: snapshot.repository_initialized ?? true,
    commits: snapshot.commits ?? [],
    branches,
    head,
    staging: snapshot.staging ?? {},
    working_tree: snapshot.working_tree ?? {},
    conflicts: snapshot.conflicts ?? [],
    remotes: snapshot.remotes ?? {},
    remote_branches: snapshot.remote_branches ?? {},
    upstream_tracking: snapshot.upstream_tracking ?? {},
    stash_stack: snapshot.stash_stack ?? [],
    reflog: snapshot.reflog ?? [],
    partial_hunks: snapshot.partial_hunks ?? {},
    replaced_commits: snapshot.replaced_commits ?? {},
    operation_metadata: snapshot.operation_metadata ?? {},
  }
}

function refsForCommit(snapshot: RepositorySnapshot, commitId: string): RefLabel[] {
  const local = Object.entries(snapshot.branches)
    .filter(([, target]) => target === commitId)
    .map(([name]) => ({ name, kind: 'local' as const }))
  const remote = Object.entries(snapshot.remote_branches ?? {})
    .filter(([, target]) => target === commitId)
    .map(([name]) => ({ name, kind: 'remote' as const }))
  return [...local, ...remote].sort((left, right) => {
    if (left.kind !== right.kind) return left.kind === 'local' ? -1 : 1
    return left.name.localeCompare(right.name)
  })
}

function headTargetFromBranches(snapshot: RepositorySnapshot) {
  if (snapshot.head.type !== 'branch') return snapshot.head.target ?? null
  return snapshot.branches[snapshot.head.name ?? ''] ?? null
}

function shortenHash(hash: string) {
  return hash.length > 7 ? hash.slice(0, 7) : hash
}

function orderRefs(refs: RefLabel[], activeRef: string | null) {
  if (!activeRef) return refs
  return [...refs].sort((left, right) => {
    if (left.name === activeRef) return -1
    if (right.name === activeRef) return 1
    if (left.kind !== right.kind) return left.kind === 'local' ? -1 : 1
    return left.name.localeCompare(right.name)
  })
}

function formatPaths(paths: string[]) {
  if (!paths.length) return 'none'
  if (paths.length <= 3) return paths.join(', ')
  return `${paths.slice(0, 3).join(', ')} +${paths.length - 3}`
}

function formatTokens(value?: RepositoryValue) {
  const tokens = tokensFor(value)
  return tokens.length ? ` (${tokens.join(', ')})` : ''
}

function tokensFor(value?: RepositoryValue): string[] {
  if (value === null || value === undefined) return []
  if (Array.isArray(value)) return value.flatMap(tokensFor)
  if (typeof value === 'object') {
    const direct = ['hunks', 'tokens', 'target_hunks', 'leftover_hunks']
      .flatMap((key) => tokensFor(value[key]))
      .filter(Boolean)
    if (direct.length) return direct
    return ['after', 'content', 'value'].flatMap((key) => tokensFor(value[key])).filter(Boolean)
  }
  const text = String(value)
  return text.includes('-hunk') || text.includes('-token') ? [text] : []
}

function formatValue(value?: RepositoryValue): string {
  if (value === null || value === undefined) return ''
  if (Array.isArray(value)) return value.map(formatValue).filter(Boolean).join(', ')
  if (typeof value === 'object') {
    const status = typeof value.status === 'string' ? value.status : ''
    const tokens = formatTokens(value)
    if (status || tokens) return `${status || 'value'}${tokens}`
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${formatValue(item)}`)
      .join(', ')
  }
  return String(value)
}

function entryStatus(value?: RepositoryValue) {
  if (value && typeof value === 'object' && !Array.isArray(value) && typeof value.status === 'string') {
    return value.status.toLowerCase()
  }
  return String(value ?? '').toLowerCase()
}
