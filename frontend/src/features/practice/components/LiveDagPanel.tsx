import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { useMemo } from 'react'
import ReactFlow, { Background, Controls, Position } from 'reactflow'
import type { Edge, Node } from 'reactflow'

import type { RepositorySnapshot } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

type GraphInput = Pick<RepositorySnapshot, 'commits' | 'branches' | 'head'> &
  Partial<Pick<RepositorySnapshot, 'working_tree' | 'staging' | 'conflicts'>>

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
          nodes={nodes}
          edges={edges}
          fitView
          fitViewOptions={{ padding: 0.12 }}
          nodesDraggable={false}
          nodesConnectable={false}
          panOnScroll
          minZoom={0.45}
          maxZoom={1.6}
          onError={handleReactFlowError}
        >
          <Background gap={18} color="rgba(255,255,255,0.05)" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </CardContent>
    </Card>
  )
}

function buildGraph(snapshot: GraphInput): { nodes: Node[]; edges: Edge[] } {
  const graph = new dagre.graphlib.Graph()
  graph.setDefaultEdgeLabel(() => ({}))
  graph.setGraph({ rankdir: 'TB', nodesep: 56, ranksep: 76 })

  if (!snapshot.commits.length) {
    const branchLabels = Object.entries(snapshot.branches)
      .filter(([, target]) => target === null)
      .map(([name]) => name)
    const workingTreeCount = Object.keys(snapshot.working_tree ?? {}).length
    const stagedCount = Object.keys(snapshot.staging ?? {}).length
    const conflictCount = snapshot.conflicts?.length ?? 0
    const stateLabels = [
      branchLabels.join(', ') || 'unborn branch',
      snapshot.head.target === null ? 'HEAD' : null,
      workingTreeCount ? `${workingTreeCount} working change${workingTreeCount === 1 ? '' : 's'}` : null,
      stagedCount ? `${stagedCount} staged` : null,
      conflictCount ? `${conflictCount} conflict${conflictCount === 1 ? '' : 's'}` : null,
    ].filter(Boolean)
    graph.setNode('__empty__', { width: 180, height: 96 })
    dagre.layout(graph)
    const point = graph.node('__empty__')

    return {
      nodes: [
        {
          id: '__empty__',
          position: { x: point.x - 90, y: point.y - 48 },
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
          data: { label: `No commits yet\n${stateLabels.join('\n')}` },
          style: {
            width: 180,
            borderRadius: 8,
            border: '1px solid hsl(var(--primary))',
            background: 'rgba(0,214,143,0.12)',
            color: 'hsl(var(--foreground))',
            fontFamily: 'JetBrains Mono, ui-monospace, monospace',
            fontSize: 12,
            lineHeight: 1.35,
            whiteSpace: 'pre-line',
            textAlign: 'left',
          },
        },
      ],
      edges: [],
    }
  }

  const nodes: Node[] = snapshot.commits.map((commit) => {
    const branchLabels = Object.entries(snapshot.branches)
      .filter(([, target]) => target === commit.id)
      .map(([name]) => name)
    const isHead = snapshot.head.target === commit.id
    const label = `${commit.id}\n${commit.message}${branchLabels.length ? `\n${branchLabels.join(', ')}` : ''}${isHead ? '\nHEAD' : ''}`
    graph.setNode(commit.id, { width: 168, height: 86 })
    return {
      id: commit.id,
      position: { x: 0, y: 0 },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: { label },
      style: {
        width: 168,
        borderRadius: 8,
        border: isHead ? '1px solid hsl(var(--primary))' : '1px solid hsl(var(--border))',
        background: isHead ? 'rgba(0,214,143,0.12)' : 'hsl(var(--secondary))',
        color: 'hsl(var(--foreground))',
        fontFamily: 'JetBrains Mono, ui-monospace, monospace',
        fontSize: 12,
        lineHeight: 1.35,
        whiteSpace: 'pre-line',
        textAlign: 'left',
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
        animated: true,
        style: { stroke: 'hsl(var(--muted-foreground))' },
      })
      graph.setEdge(parent, commit.id)
    }
  }

  dagre.layout(graph)
  return {
    nodes: nodes.map((node) => {
      const point = graph.node(node.id)
      return { ...node, position: { x: point.x - 84, y: point.y - 43 } }
    }),
    edges,
  }
}
