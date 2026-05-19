import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { memo, useMemo } from 'react'
import ReactFlow, { Background, Handle, Position } from 'reactflow'
import type { Edge, Node, NodeProps } from 'reactflow'

import type { RepositorySnapshot } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

type GraphInput = Pick<RepositorySnapshot, 'commits' | 'branches' | 'head'> &
  Partial<Pick<RepositorySnapshot, 'working_tree' | 'staging' | 'conflicts'>>

type CommitNodeData = {
  hash: string
  refs: string[]
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
  snapshot: GraphInput
  className?: string
  contentClassName?: string
}) {
  const { nodes, edges } = useMemo(() => buildGraph(snapshot), [snapshot])

  return (
    <Card className={cn('min-h-0 overflow-hidden shadow-none', className)}>
      <CardHeader className="p-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <GitCommitHorizontal className="size-5 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className={cn('h-[21rem] p-0', contentClassName)}>
        <ReactFlow
          className="h-full w-full"
          style={{ height: '100%', width: '100%' }}
          nodes={nodes}
          edges={edges}
          fitView
          fitViewOptions={{ padding: 0.08 }}
          nodesDraggable={false}
          nodesConnectable={false}
          nodeTypes={commitNodeTypes}
          panOnScroll
          minZoom={0.55}
          maxZoom={1.6}
          proOptions={{ hideAttribution: true }}
          onError={handleReactFlowError}
        >
          <Background gap={18} color="rgba(255,255,255,0.05)" />
        </ReactFlow>
      </CardContent>
    </Card>
  )
}

function CommitNode({ data }: NodeProps<CommitNodeData>) {
  const visibleRefs = orderRefs(data.refs, data.activeRef).slice(0, 3)
  const hiddenRefCount = Math.max(data.refs.length - visibleRefs.length, 0)

  return (
    <div className="flex w-32 flex-col items-center gap-2">
      <Handle className="opacity-0" type="target" position={Position.Top} />
      <div
        className={cn(
          'grid size-16 place-items-center rounded-full border font-mono text-sm font-semibold shadow-sm transition-colors',
          data.isHead
            ? 'border-accent bg-accent text-accent-foreground shadow-[0_0_0_4px_hsla(var(--accent)/0.16)]'
            : 'border-border bg-card text-foreground',
        )}
      >
        {data.hash}
      </div>
      {(visibleRefs.length > 0 || data.isDetachedHead) && (
        <div className="flex max-w-32 flex-wrap justify-center gap-1">
          {data.isDetachedHead && (
            <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-0.5 text-[10px] font-semibold leading-none text-accent">
              HEAD
            </span>
          )}
          {visibleRefs.map((ref) => {
            const isActive = ref === data.activeRef
            return (
              <span
                className={cn(
                  'max-w-28 truncate rounded-full border px-2 py-0.5 text-[10px] font-medium leading-none',
                  isActive
                    ? 'border-accent/50 bg-accent/15 text-accent'
                    : 'border-border bg-secondary text-muted-foreground',
                )}
                key={ref}
                title={ref}
              >
                {ref}
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

function buildGraph(snapshot: GraphInput): { nodes: Node[]; edges: Edge[] } {
  const graph = new dagre.graphlib.Graph()
  graph.setDefaultEdgeLabel(() => ({}))
  graph.setGraph({ rankdir: 'TB', nodesep: 44, ranksep: 80 })

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

  const nodeSizes = new Map<string, { width: number; height: number }>()
  const nodes: Node<CommitNodeData>[] = snapshot.commits.map((commit) => {
    const refs = Object.entries(snapshot.branches)
      .filter(([, target]) => target === commit.id)
      .map(([name]) => name)
      .sort()
    const isHead = snapshot.head.target === commit.id
    const activeRef = snapshot.head.type === 'branch' && isHead ? (snapshot.head.name ?? null) : null
    const size = { width: 128, height: refs.length || (isHead && snapshot.head.type === 'detached') ? 98 : 72 }
    nodeSizes.set(commit.id, size)
    graph.setNode(commit.id, size)

    return {
      id: commit.id,
      type: 'commit',
      position: { x: 0, y: 0 },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        hash: shortenHash(commit.id),
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
      const size = nodeSizes.get(node.id) ?? { width: 128, height: 72 }
      return { ...node, position: { x: point.x - size.width / 2, y: point.y - size.height / 2 } }
    }),
    edges,
  }
}

function shortenHash(hash: string) {
  return hash.length > 7 ? hash.slice(0, 7) : hash
}

function orderRefs(refs: string[], activeRef: string | null) {
  if (!activeRef) return refs
  return [...refs].sort((left, right) => {
    if (left === activeRef) return -1
    if (right === activeRef) return 1
    return left.localeCompare(right)
  })
}
