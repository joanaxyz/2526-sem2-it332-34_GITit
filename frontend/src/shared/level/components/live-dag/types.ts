import type { RepositoryCommit } from '@/shared/level/types'

export type DagVariant = 'cyan'
export type DagLayoutDirection = 'vertical' | 'horizontal'

type RefKind = 'local' | 'remote'

export type RefLabel = {
  name: string
  kind: RefKind
}

export type CommitNodeData = {
  commit: RepositoryCommit
  refs: RefLabel[]
  activeRef: string | null
  isHead: boolean
  isDetachedHead: boolean
  variant: DagVariant
  layoutDirection: DagLayoutDirection
  isActive?: boolean
  /** Commit appeared this command: play the pop-in on the node's inner div
   *  (the ReactFlow wrapper's transform is positioning - never animate it). */
  isEntering?: boolean
  /** Ref pills that just moved onto this commit: slide-up + fade. */
  enteringRefs?: string[]
  onActivate?: () => void
  onDismiss?: () => void
}

export type EmptyRepositoryNodeData = {
  branchName: string
  variant: DagVariant
}

export type EnteringDelta = {
  commits: ReadonlySet<string>
  refsByCommit: ReadonlyMap<string, string[]>
}
