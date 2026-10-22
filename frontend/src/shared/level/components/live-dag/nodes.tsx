import type { CSSProperties } from 'react'
import { Handle, Position } from 'reactflow'
import type { NodeProps } from 'reactflow'

import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

import { useCommitActivation } from './activation'
import { VARIANT_COLORS } from './constants'
import type { CommitNodeData, EmptyRepositoryNodeData, RefLabel } from './types'

export function CommitNode({ data }: NodeProps<CommitNodeData>) {
  const { activeCommitId, activate, dismiss } = useCommitActivation()
  const commitId = data.commit.id
  const isActive = activeCommitId === commitId
  const colors = VARIANT_COLORS[data.variant]
  const isHorizontal = data.layoutDirection === 'horizontal'
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
      className={cn(
        'relative z-10 flex w-36 flex-col items-center gap-2',
        data.isEntering && 'dag-node-enter',
      )}
      onMouseEnter={() => activate(commitId)}
      onMouseLeave={() => dismiss(commitId)}
      onFocus={() => activate(commitId)}
      onBlur={(event) => {
        const nextFocusTarget = event.relatedTarget
        if (!(nextFocusTarget instanceof HTMLElement) || !event.currentTarget.contains(nextFocusTarget)) {
          dismiss(commitId)
        }
      }}
    >
      <Handle className="opacity-0" type="target" position={isHorizontal ? Position.Left : Position.Top} />
      <button
        type="button"
        aria-label={label}
        title={label}
        onClick={() => activate(commitId)}
        className={cn(
          'dag-commit-seal font-mono text-sm font-semibold outline-none transition-all focus-visible:ring-2 focus-visible:ring-ring',
          data.isHead
            ? cn('is-head', colors.headNode)
            : 'text-foreground',
          isActive && 'is-inspected',
          data.enteringHead && !data.isEntering && 'is-head-arriving',
        )}
      >
        <DagSealOrnament head={data.isHead} />
        {data.isHead ? <span className="dag-head-marker">HEAD</span> : null}
        <span className="dag-commit-seal__label">{shortenHash(data.commit.id)}</span>
      </button>
      {(visibleRefs.length > 0 || data.isDetachedHead) && (
        <div className="flex max-w-36 flex-wrap justify-center gap-1">
          {data.isDetachedHead && (
            <span className={cn(
              'dag-ref-banner is-head border-accent/40 bg-accent/15 text-[11px] font-semibold leading-none text-accent',
              data.enteringHead && 'dag-ref-enter',
            )}>
              HEAD
            </span>
          )}
          {visibleRefs.map((ref) => {
            const isActive = ref.name === data.activeRef
            return (
              <span
                className={cn(
                  'dag-ref-banner max-w-32 truncate text-[11px] font-semibold leading-none',
                  isActive
                    ? cn('is-active', colors.activePill)
                    : ref.kind === 'remote'
                      ? 'is-remote text-accent'
                      : 'text-muted-foreground',
                  (data.enteringRefs?.includes(ref.name) || (isActive && data.enteringHead)) && 'dag-ref-enter',
                )}
                key={`${ref.kind}:${ref.name}`}
                title={ref.name}
              >
                {ref.name}
              </span>
            )
          })}
          {hiddenRefCount > 0 && (
            <span className="dag-ref-banner text-[11px] font-medium leading-none text-muted-foreground">
              +{hiddenRefCount}
            </span>
          )}
        </div>
      )}
      <Handle className="opacity-0" type="source" position={isHorizontal ? Position.Right : Position.Bottom} />
    </div>
  )
}

export function CommitDetailsPanel({ data }: { data: CommitNodeData | null }) {
  if (!data) return null

  const isMerge = data.commit.is_merge || data.commit.parents.length > 1

  return (
    <div
      className="commit-details-overlay pointer-events-none absolute right-3 top-3 z-50 w-60 max-w-[calc(100%-1.5rem)] overflow-hidden rounded-md border border-border/80 bg-card/90 p-3 text-left text-xs shadow-2xl shadow-black/25 backdrop-blur-md"
      data-testid="commit-details-overlay"
      role="tooltip"
    >
      <div className="flex items-center justify-between gap-2">
        <p className="font-mono text-[11px] font-semibold text-foreground">{shortenHash(data.commit.id)}</p>
        {data.isHead ? (
          <span className="shrink-0 rounded-full border border-accent/45 bg-accent/15 px-2 py-0.5 text-[11px] font-semibold leading-none text-accent">
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
            <span className="rounded-full border border-accent/35 bg-accent/10 px-2 py-0.5 text-[11px] font-medium leading-none text-accent">
              merge
            </span>
          ) : null}
          {data.refs.map((ref) => (
            <span
              key={`${ref.kind}:${ref.name}`}
              className="max-w-[10rem] truncate rounded-full border border-border bg-secondary px-2 py-0.5 text-[11px] font-medium leading-none text-muted-foreground"
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

export function EmptyRepositoryNode({ data }: NodeProps<EmptyRepositoryNodeData>) {
  const colors = VARIANT_COLORS[data.variant]
  if (!data.initialized) {
    return (
      <div className="flex w-32 flex-col items-center gap-2">
        <div className="dag-commit-seal is-void" aria-hidden="true">
          <DagSealOrnament />
        </div>
        <span className="dag-orb-caption">Git is not initialized</span>
      </div>
    )
  }
  // The burst sits beside the seal, not inside it, so the shell's shards fly
  // at full size while the new HEAD orb swells in from nothing.
  return (
    <div className={cn('relative flex w-32 flex-col items-center gap-2', data.isInitializing && 'dag-node-enter')}>
      {data.isInitializing ? <DagOrbBurst /> : null}
      <div className={cn('dag-commit-seal is-head font-mono text-xs font-semibold', colors.emptyHead)}>
        <DagSealOrnament head />
        <span className="dag-commit-seal__label">HEAD</span>
      </div>
      <span className={cn(
        'dag-ref-banner is-active max-w-28 truncate text-[11px] font-semibold leading-none',
        colors.emptyPill,
        data.isInitializing && 'dag-ref-enter',
      )}>
        {data.branchName}
      </span>
      <span className="dag-orb-caption">No commits yet</span>
    </div>
  )
}

const BURST_SHARDS = Array.from({ length: 10 }, (_, index) => index)

function DagOrbBurst() {
  return (
    <span className="dag-orb-burst" aria-hidden="true">
      {BURST_SHARDS.map((shard) => (
        <i key={shard} style={{ '--shard': shard } as CSSProperties} />
      ))}
    </span>
  )
}

function DagSealOrnament({ head = false }: { head?: boolean }) {
  // pathLength normalises the ring so its draw-on animation is size-independent.
  return (
    <svg className="dag-commit-seal__ornament" viewBox="0 0 64 64" aria-hidden="true">
      {head ? <circle className="dag-commit-seal__halo" cx="32" cy="32" r="30" /> : null}
      <circle className="dag-commit-seal__core" cx="32" cy="32" r="24" />
      <circle className="dag-commit-seal__ring" cx="32" cy="32" r="24" pathLength={1} transform="rotate(-90 32 32)" />
    </svg>
  )
}

export function RepositoryDetails({ snapshot }: { snapshot: RepositorySnapshot }) {
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
