import { useCallback, useRef, useState } from 'react'

import type { ArtifactEdit, PieceTransform } from '@/features/tower-designs/editorUtils'

/**
 * The editor's un-applied edits. The canvas renders these immediately; nothing
 * touches the server until the user hits Apply. Three independent overlays:
 *   - pendingSwaps:    pieceId -> staged piece-art asset id
 *   - pieceTransforms: pieceId -> staged free transform
 *   - artifactEdits:   placementId -> staged x/y/scale/size/rotation tweak
 */
export type StagedState = {
  pendingSwaps: Map<number, number>
  pieceTransforms: Map<number, PieceTransform>
  artifactEdits: Map<number | string, ArtifactEdit>
}

type History = { past: StagedState[]; present: StagedState; future: StagedState[] }

function emptyState(): StagedState {
  return { pendingSwaps: new Map(), pieceTransforms: new Map(), artifactEdits: new Map() }
}

export type StagedEdits = StagedState & {
  /** Apply an update. `coalesceKey` groups a continuous gesture (a drag, a burst
   *  of nudges to one field) into a single undo step; pass a fresh/empty key for
   *  discrete actions. */
  commit: (updater: (state: StagedState) => StagedState, coalesceKey?: string | null) => void
  /** Close the current coalescing window so the next commit starts a new step
   *  (call on pointer-up / input blur). */
  endGesture: () => void
  undo: () => void
  redo: () => void
  /** Drop all staged edits and history (after Apply, Discard). */
  reset: () => void
  dirtyCount: number
  canUndo: boolean
  canRedo: boolean
}

const HISTORY_LIMIT = 100

export function useStagedEdits(): StagedEdits {
  const [history, setHistory] = useState<History>(() => ({ past: [], present: emptyState(), future: [] }))
  const coalesceKey = useRef<string | null>(null)

  const commit = useCallback<StagedEdits['commit']>((updater, key = null) => {
    setHistory((current) => {
      const next = updater(current.present)
      if (next === current.present) return current
      const sameGesture = key !== null && key === coalesceKey.current && current.past.length > 0
      if (sameGesture) {
        // Mid-gesture: replace the present without opening a new history frame.
        return { ...current, present: next }
      }
      coalesceKey.current = key
      const past = [...current.past, current.present]
      if (past.length > HISTORY_LIMIT) past.shift()
      return { past, present: next, future: [] }
    })
  }, [])

  const endGesture = useCallback(() => {
    coalesceKey.current = null
  }, [])

  const undo = useCallback(() => {
    coalesceKey.current = null
    setHistory((current) => {
      if (current.past.length === 0) return current
      const past = current.past.slice(0, -1)
      const present = current.past[current.past.length - 1]
      return { past, present, future: [current.present, ...current.future] }
    })
  }, [])

  const redo = useCallback(() => {
    coalesceKey.current = null
    setHistory((current) => {
      if (current.future.length === 0) return current
      const [present, ...future] = current.future
      return { past: [...current.past, current.present], present, future }
    })
  }, [])

  const reset = useCallback(() => {
    coalesceKey.current = null
    setHistory({ past: [], present: emptyState(), future: [] })
  }, [])

  const { present } = history
  return {
    ...present,
    commit,
    endGesture,
    undo,
    redo,
    reset,
    dirtyCount: present.pendingSwaps.size + present.pieceTransforms.size + present.artifactEdits.size,
    canUndo: history.past.length > 0,
    canRedo: history.future.length > 0,
  }
}
