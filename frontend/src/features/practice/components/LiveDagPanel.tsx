import dagre from 'dagre'
import { GitCommitHorizontal } from 'lucide-react'
import { useMemo } from 'react'
import ReactFlow, { Background, Controls, Position } from 'reactflow'
import type { Edge, Node } from 'reactflow'

import type { RepositorySnapshot } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

type GraphInput = Pick<RepositorySnapshot, 'commits' | 'branches' | 'head'>

export function LiveDagPanel({ title = 'Live DAG', snapshot }: { title?: string; snapshot: GraphInput }) {
  const { nodes, edges } = useMemo(() => buildGraph(snapshot), [snapshot])

  return (
    <Card className="min-h-0 shadow-none">
      <CardHeader className="p-4">
        <CardTitle className="flex items-center gap-2 text-base">
          <GitCommitHorizontal className="size-5 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[18rem] p-0">
        <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable={false} nodesConnectable={false} panOnScroll>
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
  graph.setGraph({ rankdir: 'LR', nodesep: 44, ranksep: 80 })

  const nodes: Node[] = snapshot.commits.map((commit) => {
    const branchLabels = Object.entries(snapshot.branches)
      .filter(([, target]) => target === commit.id)
      .map(([name]) => name)
    const isHead = snapshot.head.target === commit.id
    const label = `${commit.id}\n${commit.message}${branchLabels.length ? `\n${branchLabels.join(', ')}` : ''}${isHead ? '\nHEAD' : ''}`
    graph.setNode(commit.id, { width: 150, height: 74 })
    return {
      id: commit.id,
      position: { x: 0, y: 0 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: { label },
      style: {
        width: 150,
        borderRadius: 12,
        border: isHead ? '1px solid hsl(var(--primary))' : '1px solid hsl(var(--border))',
        background: isHead ? 'rgba(0,214,143,0.12)' : 'hsl(var(--secondary))',
        color: 'hsl(var(--foreground))',
        fontFamily: 'JetBrains Mono, ui-monospace, monospace',
        fontSize: 11,
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
      return { ...node, position: { x: point.x - 75, y: point.y - 37 } }
    }),
    edges,
  }
}
