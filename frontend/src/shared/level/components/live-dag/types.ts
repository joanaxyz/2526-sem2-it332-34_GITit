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
  /** Commit appeared this command: play the pop-in on the node's inner div
   *  (the ReactFlow wrapper's transform is positioning - never animate it). */
  isEntering?: boolean
  /** Ref pills that just moved onto this commit: slide-up + fade. */
  enteringRefs?: string[]
  /** HEAD moved to this commit during the current command. */
  enteringHead?: boolean
}

export type EmptyRepositoryNodeData = {
  initialized: boolean
  branchName: string
  variant: DagVariant
  /** `git init` just ran: the hollow orb bursts into the HEAD orb. */
  isInitializing?: boolean
}

export type EnteringDelta = {
  commits: ReadonlySet<string>
  refsByCommit: ReadonlyMap<string, string[]>
  /** Commit that HEAD newly points to, including checkout at unchanged topology. */
  headTarget: string | null
  /** The repository went from an ordinary folder to initialized. */
  repositoryInitialized: boolean
}

export type DagActivity = 'idle' | 'processing' | 'updated' | 'unchanged' | 'solved' | 'error'
