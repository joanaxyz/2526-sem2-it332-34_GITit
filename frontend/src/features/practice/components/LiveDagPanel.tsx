import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { memo, useMemo, useState } from 'react'
import ReactFlow, { Background, Handle, Position } from 'reactflow'
import type { Edge, Node, NodeProps } from 'reactflow'

import type { RepositoryCommit, RepositorySnapshot } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

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
}

type EmptyRepositoryNodeData = {
  branchName: string
}

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
}: {
  title?: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
}) {
  return (
    <RepositoryStateDiagram
      title={title}
      snapshot={snapshot}
      className={className}
      contentClassName={contentClassName}
    />
  )
}

export function RepositoryStateDiagram({
  title,
  snapshot,
  className,
  contentClassName,
}: {
  title: string
  snapshot: RepositorySnapshot
  className?: string
  contentClassName?: string
}) {
  const normalizedSnapshot = useMemo(() => normalizeSnapshot(snapshot), [snapshot])
  const { nodes, edges } = useMemo(() => buildGraph(normalizedSnapshot), [normalizedSnapshot])
  const nodeTypes = useMemo(() => commitNodeTypes, [])

  return (
    <Card className={cn('min-h-0 overflow-hidden shadow-none', className)}>
      <CardHeader className="p-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <GitCommitHorizontal className="size-5 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className={cn('grid h-[21rem] grid-rows-[minmax(0,1fr)_auto] p-0', contentClassName)}>
        <ReactFlow
          className="h-full w-full"
          style={{ height: '100%', width: '100%' }}
          nodes={nodes}
          edges={edges}
          fitView
          fitViewOptions={{ padding: 0.08 }}
          nodesDraggable={false}
          nodesConnectable={false}
          nodeTypes={nodeTypes}
          panOnScroll
          minZoom={0.55}
          maxZoom={1.6}
          proOptions={{ hideAttribution: true }}
          onError={handleReactFlowError}
        >
          <Background gap={18} color="rgba(255,255,255,0.05)" />
        </ReactFlow>
        <RepositoryDetails snapshot={normalizedSnapshot} />
      </CardContent>
    </Card>
  )
}

function CommitNode({ data }: NodeProps<CommitNodeData>) {
  const [open, setOpen] = useState(false)
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
    <div className="group relative z-10 flex w-36 flex-col items-center gap-2">
      <Handle className="opacity-0" type="target" position={Position.Top} />
      <button
        type="button"
        aria-label={label}
        title={label}
        onClick={() => setOpen((value) => !value)}
        className={cn(
          'grid size-16 place-items-center rounded-full border font-mono text-sm font-semibold shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring',
          data.isHead
            ? 'border-accent bg-accent text-accent-foreground shadow-[0_0_0_4px_hsla(var(--accent)/0.16)]'
            : 'border-border bg-card text-foreground',
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
                  'max-w-32 truncate rounded-full border px-2 py-0.5 text-[10px] font-medium leading-none',
                  isActive
                    ? 'border-accent/50 bg-accent/15 text-accent'
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
      <CommitDetailsCard data={data} open={open} />
      <Handle className="opacity-0" type="source" position={Position.Bottom} />
    </div>
  )
}

function CommitDetailsCard({ data, open }: { data: CommitNodeData; open: boolean }) {
  const changedEntries = Object.entries(data.commit.changes ?? data.commit.files ?? {})
  const treeEntries = Object.entries(data.commit.tree ?? {})

  return (
    <div
      className={cn(
        'pointer-events-none absolute left-1/2 top-20 z-50 hidden max-h-80 w-80 -translate-x-1/2 overflow-auto rounded-md border border-border bg-card p-3 text-left text-xs shadow-xl group-hover:block group-focus-within:block',
        open && 'block',
      )}
      role="tooltip"
    >
      <p className="font-mono text-[11px] font-semibold text-foreground">Commit {data.commit.id}</p>
      <p className="mt-1 font-medium text-foreground">Message: {data.commit.message || '(empty)'}</p>
      <p className="mt-2 text-muted-foreground">
        Refs: {data.refs.length ? data.refs.map((ref) => ref.name).join(', ') : 'none'}
        {data.isHead ? ', HEAD' : ''}
      </p>
      <p className="text-muted-foreground">
        Parents: {data.commit.parents.length ? data.commit.parents.join(', ') : 'none'}
      </p>
      <p className="text-muted-foreground">
        Type: {data.commit.is_merge || data.commit.parents.length > 1 ? 'merge commit' : 'regular commit'}
      </p>
      <DetailList
        title="Changed paths"
        empty="No recorded path changes."
        items={changedEntries.map(([path, value]) => {
          if (typeof value === 'string') return `${value} ${path}`
          return `${value.change_type ?? 'modified'} ${path}`
        })}
      />
      <DetailList
        title="Tree"
        empty="No committed tree details."
        items={treeEntries.map(([path, value]) => `${path} @ ${String(value)}`)}
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
  return (
    <div className="flex w-32 flex-col items-center gap-2">
      <div className="grid size-16 place-items-center rounded-full border border-dashed border-accent bg-accent/15 font-mono text-xs font-semibold text-accent shadow-[0_0_0_4px_hsla(var(--accent)/0.12)]">
        HEAD
      </div>
      <span className="max-w-28 truncate rounded-full border border-accent/50 bg-accent/15 px-2 py-0.5 text-[10px] font-medium leading-none text-accent">
        {data.branchName}
      </span>
      <span className="text-center text-[11px] font-medium leading-none text-muted-foreground">No commits yet</span>
    </div>
  )
}

function RepositoryDetails({ snapshot }: { snapshot: RepositorySnapshot }) {
  const staged = Object.keys(snapshot.staging)
  const working = Object.keys(snapshot.working_tree)
  const conflicts = snapshot.conflicts
  const remotes = Object.entries(snapshot.remotes ?? {})
  const remoteBranches = Object.entries(snapshot.remote_branches ?? {})
  const stashCount = snapshot.stash_stack?.length ?? 0

  return (
    <div className="max-h-28 overflow-auto border-t border-border bg-background/95 px-3 py-2 text-[11px]">
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        <SummaryLine label="Staged" value={formatPaths(staged)} />
        <SummaryLine label="Working tree" value={formatPaths(working)} />
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
        <SummaryLine label="Stash" value={stashCount ? `${stashCount} entr${stashCount === 1 ? 'y' : 'ies'}` : 'none'} />
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

function buildGraph(snapshot: RepositorySnapshot): { nodes: Node[]; edges: Edge[] } {
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
          data: { branchName },
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

  dagre.layout(graph)
  return {
    nodes: nodes.map((node) => {
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
