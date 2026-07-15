import dagre from 'dagre'
import { Position } from 'reactflow'
import type { Edge, Node } from 'reactflow'

import type { RepositorySnapshot } from '@/shared/level/types'

import { NO_DELTA } from './constants'
import type { CommitNodeData, DagLayoutDirection, DagVariant, EnteringDelta, RefLabel } from './types'

// dagre layout is the heaviest per-command cost, but node positions depend only
// on commit topology (exactly what graphLayoutSignature captures). Cache positions
// per topology so ref/HEAD/staging-only commands (git add, branch, switch, status)
// refresh the cheap node data without re-running a full graph layout. Module level
// so the cache is shared across diagram instances (live + expected often match)
// and stays out of render-time ref/state mutation territory.
export const layoutPositionsCache = new Map<string, Map<string, { x: number; y: number }>>()
const LAYOUT_CACHE_MAX_ENTRIES = 64

/** What this command added/moved, for the enter animations. */
export function snapshotDelta(prev: RepositorySnapshot, next: RepositorySnapshot): EnteringDelta {
  const prevIds = new Set(prev.commits.map((commit) => commit.id))
  const commits = new Set(next.commits.filter((commit) => !prevIds.has(commit.id)).map((commit) => commit.id))
  const refsByCommit = new Map<string, string[]>()
  const collect = (nextRefs: Record<string, string | null>, prevRefs: Record<string, string | null>) => {
    for (const [name, target] of Object.entries(nextRefs)) {
      if (!target || prevRefs[name] === target) continue
      // Moved or newly created ref -> animate its pill on the commit it landed on.
      if (prevRefs[name] !== undefined || prev.repository_initialized) {
        refsByCommit.set(target, [...(refsByCommit.get(target) ?? []), name])
      }
    }
  }
  collect(next.branches ?? {}, prev.branches ?? {})
  collect(next.remote_branches ?? {}, prev.remote_branches ?? {})
  if (!commits.size && !refsByCommit.size) return NO_DELTA
  return { commits, refsByCommit }
}

export function rememberLayoutPositions(
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

export function buildGraph(
  snapshot: RepositorySnapshot,
  variant: DagVariant,
  layoutDirection: DagLayoutDirection,
  cachedPositions?: Map<string, { x: number; y: number }>,
): { nodes: Node[]; edges: Edge[] } {
  const graph = new dagre.graphlib.Graph()
  graph.setDefaultEdgeLabel(() => ({}))
  const isHorizontal = layoutDirection === 'horizontal'
  graph.setGraph({
    rankdir: isHorizontal ? 'LR' : 'TB',
    nodesep: isHorizontal ? 72 : 56,
    ranksep: isHorizontal ? 128 : 88,
  })

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
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      data: {
        commit,
        refs,
        activeRef,
        isHead,
        isDetachedHead: isHead && snapshot.head.type === 'detached',
        variant,
        layoutDirection,
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

export function normalizeSnapshot(snapshot: RepositorySnapshot): RepositorySnapshot {
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
