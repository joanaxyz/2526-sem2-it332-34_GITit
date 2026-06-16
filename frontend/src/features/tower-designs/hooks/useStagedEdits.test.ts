import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { ArtifactEdit, PieceTransform } from '@/features/tower-designs/editorUtils'
import { useStagedEdits, type StagedState } from './useStagedEdits'

function stageSwap(state: StagedState, pieceId: number, assetId: number): StagedState {
  const pendingSwaps = new Map(state.pendingSwaps)
  pendingSwaps.set(pieceId, assetId)
  return { ...state, pendingSwaps }
}

function stageArtifactEdit(state: StagedState, placementId: number | string, edit: ArtifactEdit): StagedState {
  const artifactEdits = new Map(state.artifactEdits)
  artifactEdits.set(placementId, edit)
  return { ...state, artifactEdits }
}

function stagePieceTransform(state: StagedState, pieceId: number, transform: PieceTransform): StagedState {
  const pieceTransforms = new Map(state.pieceTransforms)
  pieceTransforms.set(pieceId, transform)
  return { ...state, pieceTransforms }
}

function transform(x: number): PieceTransform {
  return { x, y: 0, scaleX: 1, scaleY: 1, rotation: 0, zIndex: 0 }
}

describe('useStagedEdits', () => {
  it('restores staged edit mementos through undo and redo', () => {
    const { result } = renderHook(() => useStagedEdits())

    act(() => result.current.commit((state) => stageSwap(state, 7, 101)))
    act(() => result.current.commit((state) => stageArtifactEdit(state, 'draft-artifact', { x: 24, y: 36 })))

    expect(result.current.pendingSwaps.get(7)).toBe(101)
    expect(result.current.artifactEdits.get('draft-artifact')).toEqual({ x: 24, y: 36 })
    expect(result.current.dirtyCount).toBe(2)

    act(() => result.current.undo())

    expect(result.current.pendingSwaps.get(7)).toBe(101)
    expect(result.current.artifactEdits.has('draft-artifact')).toBe(false)
    expect(result.current.canRedo).toBe(true)

    act(() => result.current.redo())

    expect(result.current.pendingSwaps.get(7)).toBe(101)
    expect(result.current.artifactEdits.get('draft-artifact')).toEqual({ x: 24, y: 36 })
    expect(result.current.canRedo).toBe(false)
  })

  it('coalesces repeated gesture commits into one undo memento', () => {
    const { result } = renderHook(() => useStagedEdits())

    act(() => result.current.commit((state) => stagePieceTransform(state, 4, transform(1)), 'piece:4'))
    act(() => result.current.commit((state) => stagePieceTransform(state, 4, transform(12)), 'piece:4'))
    act(() => result.current.endGesture())
    act(() => result.current.commit((state) => stagePieceTransform(state, 4, transform(20)), 'piece:4'))

    expect(result.current.pieceTransforms.get(4)?.x).toBe(20)

    act(() => result.current.undo())

    expect(result.current.pieceTransforms.get(4)?.x).toBe(12)

    act(() => result.current.undo())

    expect(result.current.pieceTransforms.has(4)).toBe(false)
    expect(result.current.dirtyCount).toBe(0)
  })

  it('clears redo mementos when a new edit follows undo', () => {
    const { result } = renderHook(() => useStagedEdits())

    act(() => result.current.commit((state) => stageSwap(state, 1, 10)))
    act(() => result.current.commit((state) => stageSwap(state, 1, 20)))
    act(() => result.current.undo())

    expect(result.current.pendingSwaps.get(1)).toBe(10)
    expect(result.current.canRedo).toBe(true)

    act(() => result.current.commit((state) => stageSwap(state, 1, 30)))

    expect(result.current.pendingSwaps.get(1)).toBe(30)
    expect(result.current.canRedo).toBe(false)

    act(() => result.current.redo())

    expect(result.current.pendingSwaps.get(1)).toBe(30)
  })

  it('does not create history frames for unchanged mementos', () => {
    const { result } = renderHook(() => useStagedEdits())

    act(() => result.current.commit((state) => ({ ...state, pendingSwaps: new Map(state.pendingSwaps) })))

    expect(result.current.canUndo).toBe(false)
    expect(result.current.dirtyCount).toBe(0)
  })

  it('keeps mementos isolated from mutating updaters and external objects', () => {
    const { result } = renderHook(() => useStagedEdits())

    act(() => {
      result.current.commit((state) => {
        ;(state.pendingSwaps as Map<number, number>).set(9, 90)
        return state
      })
    })

    expect(result.current.pendingSwaps.get(9)).toBe(90)

    act(() => result.current.undo())

    expect(result.current.pendingSwaps.has(9)).toBe(false)

    const externalTransform = transform(3)
    act(() => result.current.commit((state) => stagePieceTransform(state, 2, externalTransform)))
    externalTransform.x = 999

    expect(result.current.pieceTransforms.get(2)?.x).toBe(3)

    act(() => result.current.undo())
    act(() => result.current.redo())

    expect(result.current.pieceTransforms.get(2)?.x).toBe(3)
  })
})
