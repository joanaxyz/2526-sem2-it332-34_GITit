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
  pendingSwaps: ReadonlyMap<number, number>
  pieceTransforms: ReadonlyMap<number, PieceTransform>
  artifactEdits: ReadonlyMap<number | string, ArtifactEdit>
}

type StagedMemento = {
  pendingSwaps: readonly (readonly [number, number])[]
  pieceTransforms: readonly (readonly [number, PieceTransform])[]
  artifactEdits: readonly (readonly [number | string, ArtifactEdit])[]
}

type History = { past: StagedMemento[]; present: StagedState; future: StagedMemento[] }

function emptyState(): StagedState {
  return { pendingSwaps: new Map(), pieceTransforms: new Map(), artifactEdits: new Map() }
}

function clonePieceTransform(transform: PieceTransform): PieceTransform {
  return { ...transform }
}

function cloneArtifactEdit(edit: ArtifactEdit): ArtifactEdit {
  return { ...edit }
}

function cloneState(state: StagedState): StagedState {
  return {
    pendingSwaps: new Map(state.pendingSwaps),
    pieceTransforms: new Map(
      [...state.pieceTransforms].map(([id, transform]) => [id, clonePieceTransform(transform)]),
    ),
    artifactEdits: new Map([...state.artifactEdits].map(([id, edit]) => [id, cloneArtifactEdit(edit)])),
  }
}

function createMemento(state: StagedState): StagedMemento {
  return {
    pendingSwaps: [...state.pendingSwaps],
    pieceTransforms: [...state.pieceTransforms].map(([id, transform]) => [id, clonePieceTransform(transform)]),
    artifactEdits: [...state.artifactEdits].map(([id, edit]) => [id, cloneArtifactEdit(edit)]),
  }
}

function restoreMemento(memento: StagedMemento): StagedState {
  return {
    pendingSwaps: new Map(memento.pendingSwaps),
    pieceTransforms: new Map(
      memento.pieceTransforms.map(([id, transform]) => [id, clonePieceTransform(transform)]),
    ),
    artifactEdits: new Map(memento.artifactEdits.map(([id, edit]) => [id, cloneArtifactEdit(edit)])),
  }
}

function appendPast(past: StagedMemento[], memento: StagedMemento): StagedMemento[] {
  const next = [...past, memento]
  if (next.length > HISTORY_LIMIT) next.shift()
  return next
}

function stagedStatesEqual(a: StagedState, b: StagedState): boolean {
  return (
    primitiveMapsEqual(a.pendingSwaps, b.pendingSwaps) &&
    pieceTransformMapsEqual(a.pieceTransforms, b.pieceTransforms) &&
    artifactEditMapsEqual(a.artifactEdits, b.artifactEdits)
  )
}

function primitiveMapsEqual<K, V>(a: ReadonlyMap<K, V>, b: ReadonlyMap<K, V>): boolean {
  if (a.size !== b.size) return false
  for (const [key, value] of a) {
    if (b.get(key) !== value) return false
  }
  return true
}

function pieceTransformMapsEqual(a: ReadonlyMap<number, PieceTransform>, b: ReadonlyMap<number, PieceTransform>): boolean {
  if (a.size !== b.size) return false
  for (const [key, value] of a) {
    const other = b.get(key)
    if (
      !other ||
      value.x !== other.x ||
      value.y !== other.y ||
      value.scaleX !== other.scaleX ||
      value.scaleY !== other.scaleY ||
      value.rotation !== other.rotation ||
      value.zIndex !== other.zIndex
    ) {
      return false
    }
  }
  return true
}

function artifactEditMapsEqual(
  a: ReadonlyMap<number | string, ArtifactEdit>,
  b: ReadonlyMap<number | string, ArtifactEdit>,
): boolean {
  if (a.size !== b.size) return false
  for (const [key, value] of a) {
    const other = b.get(key)
    if (
      !other ||
      value.x !== other.x ||
      value.y !== other.y ||
      value.scale !== other.scale ||
      value.rotation !== other.rotation ||
      value.width !== other.width ||
      value.height !== other.height ||
      value.zIndex !== other.zIndex ||
      value.targetInstanceId !== other.targetInstanceId
    ) {
      return false
    }
  }
  return true
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
      const next = cloneState(updater(cloneState(current.present)))
      if (stagedStatesEqual(next, current.present)) return current
      const sameGesture = key !== null && key === coalesceKey.current && current.past.length > 0
      if (sameGesture) {
        // Mid-gesture: replace the present without opening a new history frame.
        return { ...current, present: next }
      }
      coalesceKey.current = key
      const past = appendPast(current.past, createMemento(current.present))
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
      const present = restoreMemento(current.past[current.past.length - 1])
      return { past, present, future: [createMemento(current.present), ...current.future] }
    })
  }, [])

  const redo = useCallback(() => {
    coalesceKey.current = null
    setHistory((current) => {
      if (current.future.length === 0) return current
      const [presentMemento, ...future] = current.future
      return {
        past: appendPast(current.past, createMemento(current.present)),
        present: restoreMemento(presentMemento),
        future,
      }
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
