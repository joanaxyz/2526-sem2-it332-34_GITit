import { useMemo } from 'react'

import type { BookBlock, BookDiagramEdge, BookDiagramNode } from '@/features/tower-map/book/bookTypes'

const ACCENT_RGB: Record<string, string> = {
  cyan: '45, 245, 255',
  purple: '176, 74, 255',
  muted: '148, 163, 184',
}

function accentRgb(accent?: string) {
  return ACCENT_RGB[accent ?? 'cyan'] ?? ACCENT_RGB.cyan
}

// Authored diagrams render as SVG so they keep the tower's neon look at any size.
// Two kinds are understood; anything else falls back to a caption-only card.
export function BookDiagram({ block }: { block: BookBlock }) {
  const hasGraph = Array.isArray(block.nodes) && block.nodes.length > 0
  return (
    <figure className="book-diagram">
      {block.title ? <figcaption className="book-diagram-title">{block.title}</figcaption> : null}
      <div className="book-diagram-canvas">
        {block.diagram_kind === 'flow' && hasGraph ? (
          <FlowDiagram nodes={block.nodes!} edges={block.edges ?? []} />
        ) : block.diagram_kind === 'dag' && hasGraph ? (
          <DagDiagram nodes={block.nodes!} edges={block.edges ?? []} />
        ) : (
          <p className="book-diagram-empty">Diagram unavailable.</p>
        )}
      </div>
      {block.legend?.length ? (
        <ul className="book-diagram-legend">
          {block.legend.map((item) => (
            <li key={item.label}>
              <span className="book-diagram-legend-dot" style={{ background: `rgb(${accentRgb(item.accent)})` }} />
              {item.label}
            </li>
          ))}
        </ul>
      ) : null}
      {block.caption ? <p className="book-diagram-caption">{block.caption}</p> : null}
    </figure>
  )
}

function FlowDiagram({ nodes, edges }: { nodes: BookDiagramNode[]; edges: BookDiagramEdge[] }) {
  const boxW = 132
  const boxH = 64
  const gap = 64
  const padX = 14
  const padY = 30
  const width = padX * 2 + nodes.length * boxW + (nodes.length - 1) * gap
  const height = padY * 2 + boxH
  const xOf = (index: number) => padX + index * (boxW + gap)
  const centerY = padY + boxH / 2
  const indexById = new Map(nodes.map((node, index) => [node.id, index]))

  return (
    <svg className="book-diagram-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Flow diagram">
      <defs>
        <marker id="book-flow-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
          <path d="M0 0 L9 4.5 L0 9 Z" fill="rgba(126, 249, 255, 0.85)" />
        </marker>
      </defs>
      {edges.map((edge) => {
        const from = indexById.get(edge.from)
        const to = indexById.get(edge.to)
        if (from === undefined || to === undefined) return null
        const x1 = xOf(from) + boxW
        const x2 = xOf(to)
        const midX = (x1 + x2) / 2
        return (
          <g key={`${edge.from}-${edge.to}`}>
            <line
              x1={x1}
              y1={centerY}
              x2={x2 - 4}
              y2={centerY}
              stroke="rgba(126, 249, 255, 0.5)"
              strokeWidth={1.6}
              markerEnd="url(#book-flow-arrow)"
            />
            {edge.label ? (
              <text x={midX} y={centerY - 10} className="book-diagram-edge-label" textAnchor="middle">
                {edge.label}
              </text>
            ) : null}
          </g>
        )
      })}
      {nodes.map((node, index) => {
        const rgb = accentRgb(node.accent)
        return (
          <g key={node.id} transform={`translate(${xOf(index)}, ${padY})`}>
            <rect
              width={boxW}
              height={boxH}
              rx={10}
              fill={`rgba(${rgb}, 0.1)`}
              stroke={`rgba(${rgb}, 0.55)`}
              strokeWidth={1.4}
            />
            <text x={boxW / 2} y={boxH / 2 + 4} className="book-diagram-node-label" textAnchor="middle">
              {node.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

function DagDiagram({ nodes, edges }: { nodes: BookDiagramNode[]; edges: BookDiagramEdge[] }) {
  // Column = longest path from a root, so a branch/merge reads as a diamond.
  const columns = useMemo(() => assignColumns(nodes, edges), [nodes, edges])
  const colGap = 96
  const laneGap = 76
  const radius = 18
  const padX = 40
  const padY = 40
  const maxCol = Math.max(0, ...nodes.map((node) => columns.get(node.id) ?? 0))
  const maxLane = Math.max(0, ...nodes.map((node) => node.lane ?? 0))
  const width = padX * 2 + maxCol * colGap
  const height = padY * 2 + maxLane * laneGap
  const xOf = (id: string) => padX + (columns.get(id) ?? 0) * colGap
  const yOf = (lane: number) => padY + lane * laneGap
  const laneById = new Map(nodes.map((node) => [node.id, node.lane ?? 0]))
  const accentForLane = (lane: number) => (lane === 0 ? ACCENT_RGB.cyan : ACCENT_RGB.purple)

  return (
    <svg className="book-diagram-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Commit graph">
      {edges.map((edge) => {
        const fromLane = laneById.get(edge.from)
        const toLane = laneById.get(edge.to)
        if (fromLane === undefined || toLane === undefined) return null
        const x1 = xOf(edge.from)
        const y1 = yOf(fromLane)
        const x2 = xOf(edge.to)
        const y2 = yOf(toLane)
        const accent = accentForLane(toLane)
        const midX = (x1 + x2) / 2
        return (
          <path
            key={`${edge.from}-${edge.to}`}
            d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
            fill="none"
            stroke={`rgba(${accent}, 0.6)`}
            strokeWidth={2}
          />
        )
      })}
      {nodes.map((node) => {
        const lane = node.lane ?? 0
        const rgb = node.type === 'merge' ? ACCENT_RGB.purple : accentForLane(lane)
        const cx = xOf(node.id)
        const cy = yOf(lane)
        return (
          <g key={node.id}>
            <circle
              cx={cx}
              cy={cy}
              r={radius}
              fill={`rgba(${rgb}, 0.16)`}
              stroke={`rgb(${rgb})`}
              strokeWidth={node.type === 'merge' ? 2.6 : 1.8}
            />
            <text x={cx} y={cy + 4} className="book-diagram-node-label" textAnchor="middle">
              {node.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

function assignColumns(nodes: BookDiagramNode[], edges: BookDiagramEdge[]): Map<string, number> {
  const columns = new Map<string, number>(nodes.map((node) => [node.id, 0]))
  // Relax edges repeatedly; the graph is tiny so a bounded sweep is plenty.
  for (let pass = 0; pass < nodes.length; pass += 1) {
    let changed = false
    for (const edge of edges) {
      const fromCol = columns.get(edge.from) ?? 0
      const toCol = columns.get(edge.to) ?? 0
      if (toCol < fromCol + 1) {
        columns.set(edge.to, fromCol + 1)
        changed = true
      }
    }
    if (!changed) break
  }
  return columns
}
