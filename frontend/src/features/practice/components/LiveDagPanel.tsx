import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import ReactFlow, { Background, Handle, Position, ReactFlowProvider, useReactFlow } from 'reactflow'
import type { Edge, Node, NodeProps } from 'reactflow'

import type { RepositoryCommit, RepositorySnapshot, RepositoryValue } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

type DagVariant = 'cyan' | 'violet'

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
  violet: {
    border: 'rgba(168,85,247,0.42)',
    headerBg: 'rgba(168,85,247,0.025)',
    iconShadow: 'drop-shadow(0 0 4px rgba(168,85,247,0.55))',
    titleClass: 'text-purple-500',
    gradientBg: 'radial-gradient(ellipse at 30% 40%, rgba(168,85,247,0.05) 0%, transparent 62%)',
    dotColor: 'rgba(168,85,247,0.06)',
    headNode: 'border-2 border-purple-500 bg-purple-500/15 text-purple-500 dag-head-glow-violet',
    activePill: 'border-purple-500/55 bg-purple-500/10 text-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.22)]',
    emptyHead: 'dag-head-glow-violet border-2 border-dashed border-purple-500 bg-purple-500/10 text-purple-500',
    emptyPill: 'border-purple-500/50 bg-purple-500/10 text-purple-500 shadow-[0_0_6px_rgba(168,85,247,0.2)]',
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
}: {
  title?: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
}) {
  return (
    <RepositoryStateDiagram
      title={title}
      snapshot={snapshot}
      className={className}
      contentClassName={contentClassName}
      showRepositoryDetails={showRepositoryDetails}
      fitViewPadding={fitViewPadding}
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
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
}) {
  const colors = VARIANT_COLORS[variant]
  // #region agent log
  fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'4d73ce'},body:JSON.stringify({sessionId:'4d73ce',location:'LiveDagPanel.tsx:RepositoryStateDiagramBody',message:'diagram body mount',data:{hypothesisId:'E',variantProp:variant,commitsCount:snapshot.commits?.length??0},timestamp:Date.now(),runId:'post-fix'})}).catch(()=>{});
  // #endregion
  const normalizedSnapshot = useMemo(() => normalizeSnapshot(snapshot), [snapshot])
  const layoutSignature = useMemo(() => graphLayoutSignature(normalizedSnapshot), [normalizedSnapshot])
  const layoutCacheRef = useRef<{ signature: string; positions: Map<string, { x: number; y: number }> } | null>(
    null,
  )
  const { nodes, edges } = useMemo(() => {
    const cached = layoutCacheRef.current
    if (cached?.signature === layoutSignature) {
      return buildGraph(normalizedSnapshot, variant, cached.positions)
    }
    const graph = buildGraph(normalizedSnapshot, variant)
    layoutCacheRef.current = {
      signature: layoutSignature,
      positions: new Map(graph.nodes.map((node) => [node.id, node.position])),
    }
    return graph
  }, [layoutSignature, normalizedSnapshot, variant])
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
        <div className="flex flex-wrap items-center gap-2">
          <GitCommitHorizontal
            className="size-4"
            style={{ filter: colors.iconShadow, color: variant === 'violet' ? 'rgb(168,85,247)' : undefined }}
          />
          <span className={cn('text-sm font-bold tracking-wide', colors.titleClass)}>{title}</span>
          {normalizedSnapshot.commits.length > 0 && (
            <span className="text-[10px] font-normal text-muted-foreground/65">
              Hover or click a commit for details.
            </span>
          )}
        </div>
        {!normalizedSnapshot.commits.length && (
          <p className="mt-0.5 text-[10px] text-muted-foreground/50">
            No commit metadata yet.
          </p>
        )}
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
            minZoom={0.55}
            maxZoom={1.6}
            proOptions={{ hideAttribution: true }}
            onError={handleReactFlowError}
          >
            <Background gap={18} color="rgba(255,255,255,0.05)" />
            <FitViewOnTopologyChange layoutSignature={layoutSignature} fitViewPadding={fitViewPadding} />
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
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
  showRepositoryDetails?: boolean
  fitViewPadding?: number
  variant?: DagVariant
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
      />
    </ReactFlowProvider>
  )
}

function FitViewOnTopologyChange({
  layoutSignature,
  fitViewPadding,
}: {
  layoutSignature: string
  fitViewPadding: number
}) {
  const { fitView } = useReactFlow()
  const previousSignature = useRef<string | null>(null)

  useEffect(() => {
    if (previousSignature.current === layoutSignature) return
    previousSignature.current = layoutSignature
    const frameId = window.requestAnimationFrame(() => {
      void fitView({ padding: fitViewPadding, duration: 0 })
    })
    return () => window.cancelAnimationFrame(frameId)
  }, [fitView, fitViewPadding, layoutSignature])

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

  const changedEntries = Object.entries(data.commit.changes ?? data.commit.files ?? {})
  const treeEntries = Object.entries(data.commit.tree ?? {})

  return (
    <div
      className="pointer-events-none absolute right-3 top-3 z-50 max-h-[calc(100%-1.5rem)] w-72 max-w-[calc(100%-1.5rem)] overflow-hidden rounded-md border border-border/80 bg-card/85 p-3 text-left text-xs shadow-2xl shadow-black/25 backdrop-blur-md"
      data-testid="commit-details-overlay"
      role="tooltip"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-mono text-[11px] font-semibold text-foreground">Commit {data.commit.id}</p>
          <p className="mt-1 truncate font-medium text-foreground" title={data.commit.message || '(empty)'}>
            Message: {data.commit.message || '(empty)'}
          </p>
        </div>
        {data.isHead ? (
          <span className="shrink-0 rounded-full border border-accent/45 bg-accent/15 px-2 py-0.5 text-[10px] font-semibold leading-none text-accent">
            HEAD
          </span>
        ) : null}
      </div>
      <div className="mt-2 space-y-0.5 text-muted-foreground">
        <p className="truncate" title={data.refs.length ? data.refs.map((ref) => ref.name).join(', ') : 'none'}>
          Refs: {data.refs.length ? data.refs.map((ref) => ref.name).join(', ') : 'none'}
        </p>
        <p className="truncate" title={data.commit.parents.length ? data.commit.parents.join(', ') : 'none'}>
          Parents: {data.commit.parents.length ? data.commit.parents.join(', ') : 'none'}
        </p>
        <p>Type: {data.commit.is_merge || data.commit.parents.length > 1 ? 'merge commit' : 'regular commit'}</p>
      </div>
      <DetailList
        title="Changed paths"
        empty="No recorded path changes."
        items={changedEntries.map(([path, value]) => {
          if (typeof value === 'string') return `${value} ${path}`
          if (!value || typeof value !== 'object' || Array.isArray(value)) return `${formatValue(value)} ${path}`
          const changeType = typeof value.change_type === 'string' ? value.change_type : 'modified'
          return `${changeType} ${path}${formatTokens(value.after)}`
        })}
      />
      <DetailList
        title="Tree"
        empty="No committed tree details."
        items={treeEntries.map(([path, value]) => `${path} @ ${formatValue(value)}`)}
        limit={8}
      />
    </div>
  )
}

function DetailList({
  title,
  empty,
  items,
  limit = 6,
}: {
  title: string
  empty: string
  items: string[]
  limit?: number
}) {
  const visible = items.slice(0, limit)
  const remaining = items.length - visible.length
  return (
    <div className="mt-2">
      <p className="font-semibold text-foreground">{title}:</p>
      {visible.length ? (
        <ul className="mt-1 space-y-0.5 text-muted-foreground">
          {visible.map((item) => (
            <li className="truncate" key={item} title={item}>
              {item}
            </li>
          ))}
          {remaining > 0 ? <li>+{remaining} more</li> : null}
        </ul>
      ) : (
        <p className="mt-1 text-muted-foreground">{empty}</p>
      )}
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

export function graphLayoutSignature(snapshot: RepositorySnapshot): string {
  if (!snapshot.commits.length) return 'empty'
  const commitIds = snapshot.commits
    .map((commit) => commit.id)
    .sort()
    .join(',')
  const edges = snapshot.commits
    .flatMap((commit) => (commit.parents ?? []).map((parent) => `${parent}->${commit.id}`))
    .sort()
    .join(',')
  return `${commitIds}|${edges}`
}

function buildGraph(
  snapshot: RepositorySnapshot,
  variant: DagVariant,
  cachedPositions?: Map<string, { x: number; y: number }>,
): { nodes: Node[]; edges: Edge[] } {
  // #region agent log
  fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'4d73ce'},body:JSON.stringify({sessionId:'4d73ce',location:'LiveDagPanel.tsx:buildGraph',message:'buildGraph entry',data:{hypothesisId:'A',variantParam:variant,commitsLength:snapshot.commits.length,emptyRepo:!snapshot.commits.length,hasCachedPositions:Boolean(cachedPositions)},timestamp:Date.now(),runId:'post-fix'})}).catch(()=>{});
  // #endregion
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
