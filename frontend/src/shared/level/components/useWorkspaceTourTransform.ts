import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  KeyboardEvent as ReactKeyboardEvent,
  PointerEvent as ReactPointerEvent,
} from 'react'

import { VIEWPORT_GAP, type RectSnapshot } from './gameplayWorkspaceTourLayout'
import type {
  WorkspaceTourPane as Pane,
  WorkspaceTourPosition as Position,
  WorkspaceTourSize as Size,
} from './gameplayWorkspaceTourTypes'

type PaneBounds = { size: Size; minimum: Size; maximum: Size }

type TransformMode = 'move' | 'resize'

type TransformSession = {
  mode: 'move'
  pane: Pane
  pointerId: number
  startX: number
  startY: number
  frame: RectSnapshot
} | {
  mode: 'resize'
  pane: Pane
  pointerId: number
  startX: number
  startY: number
  bounds: PaneBounds
}

const TRANSFORM_BREAKPOINT = 600
const PANE_MINIMUMS: Record<Pane, Size> = {
  main: { width: 304, height: 220 },
  aside: { width: 240, height: 160 },
}
const KEYBOARD_TRANSFORM_STEP = 16

export function workspaceTourFrame(position: Position, size: Size): RectSnapshot {
  return {
    left: position.left,
    top: position.top,
    right: position.left + size.width,
    bottom: position.top + size.height,
    width: size.width,
    height: size.height,
  }
}

function clampPosition(position: Position, size: Size): Position {
  return {
    left: Math.min(
      Math.max(position.left, VIEWPORT_GAP),
      Math.max(VIEWPORT_GAP, window.innerWidth - size.width - VIEWPORT_GAP),
    ),
    top: Math.min(
      Math.max(position.top, VIEWPORT_GAP),
      Math.max(VIEWPORT_GAP, window.innerHeight - size.height - VIEWPORT_GAP),
    ),
  }
}

function clampSize(size: Size, { minimum, maximum }: PaneBounds): Size {
  const clamp = (value: number, low: number, high: number) => Math.min(Math.max(value, Math.min(low, high)), high)
  return {
    width: clamp(size.width, minimum.width, maximum.width),
    height: clamp(size.height, minimum.height, maximum.height),
  }
}

/** Arrow keys as a step, farther with Shift; null for any other key. */
function arrowDelta(event: ReactKeyboardEvent) {
  const step = event.shiftKey ? KEYBOARD_TRANSFORM_STEP * 3 : KEYBOARD_TRANSFORM_STEP
  switch (event.key) {
    case 'ArrowLeft': return { dx: -step, dy: 0 }
    case 'ArrowRight': return { dx: step, dy: 0 }
    case 'ArrowUp': return { dx: 0, dy: -step }
    case 'ArrowDown': return { dx: 0, dy: step }
    default: return null
  }
}

export function useWorkspaceTourTransform({
  cardElement,
  separate,
  transformable,
  activeStepId,
  refreshKey,
}: {
  cardElement: HTMLElement | null
  separate: boolean
  transformable: boolean
  activeStepId?: string
  refreshKey?: string | number
}) {
  const [panePositions, setPanePositions] = useState<Partial<Record<Pane, Position>>>({})
  const [paneSizes, setPaneSizes] = useState<Partial<Record<Pane, Size>>>({})
  const [frontPane, setFrontPane] = useState<Pane>('main')
  const [transformMode, setTransformMode] = useState<TransformMode | null>(null)
  const transformSessionRef = useRef<TransformSession | null>(null)
  const transformed = Object.values(panePositions).some(Boolean) || Object.values(paneSizes).some(Boolean)

  const resetTransform = useCallback(() => {
    setPanePositions({})
    setPaneSizes({})
  }, [])

  const resetPane = useCallback((pane: Pane) => {
    setPanePositions((positions) => ({ ...positions, [pane]: undefined }))
    setPaneSizes((sizes) => ({ ...sizes, [pane]: undefined }))
  }, [])

  const paneElement = useCallback((pane: Pane) => (
    separate
      ? cardElement?.querySelector<HTMLElement>(`[data-tour-pane="${pane}"]`) ?? null
      : cardElement
  ), [cardElement, separate])

  /** Where a card sits: pinned once moved or resized, else wherever layout put it. */
  const paneFrame = useCallback((pane: Pane): RectSnapshot | null => {
    const rect = paneElement(pane)?.getBoundingClientRect()
    if (!rect) return null
    return workspaceTourFrame(panePositions[pane] ?? rect, paneSizes[pane] ?? rect)
  }, [paneElement, panePositions, paneSizes])

  /** The first transform pins every card so only the active card then changes. */
  const pinPanes = useCallback(() => {
    const pinned: Partial<Record<Pane, Position>> = {}
    for (const pane of separate ? ['main', 'aside'] as const : ['main'] as const) {
      const frame = paneFrame(pane)
      if (frame) pinned[pane] = { left: frame.left, top: frame.top }
    }
    setPanePositions((positions) => ({ ...pinned, ...positions }))
  }, [paneFrame, separate])

  /** A card grows right and down from where it sits, up to the viewport edge. */
  const paneBounds = useCallback((pane: Pane): PaneBounds | null => {
    const frame = paneFrame(pane)
    if (!frame) return null
    return {
      size: { width: frame.width, height: frame.height },
      minimum: PANE_MINIMUMS[pane],
      maximum: {
        width: Math.max(1, window.innerWidth - VIEWPORT_GAP - frame.left),
        height: Math.max(1, window.innerHeight - VIEWPORT_GAP - frame.top),
      },
    }
  }, [paneFrame])

  const beginMove = useCallback((pane: Pane, event: ReactPointerEvent<HTMLButtonElement>) => {
    if (!transformable || window.innerWidth <= TRANSFORM_BREAKPOINT) return
    const frame = paneFrame(pane)
    if (!frame) return
    event.preventDefault()
    event.currentTarget.setPointerCapture?.(event.pointerId)
    transformSessionRef.current = {
      mode: 'move',
      pane,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      frame,
    }
    pinPanes()
    setPanePositions((positions) => ({ ...positions, [pane]: clampPosition(frame, frame) }))
    setFrontPane(pane)
    setTransformMode('move')
  }, [paneFrame, pinPanes, transformable])

  const beginResize = useCallback((pane: Pane, event: ReactPointerEvent<HTMLButtonElement>) => {
    if (!transformable || window.innerWidth <= TRANSFORM_BREAKPOINT) return
    const bounds = paneBounds(pane)
    if (!bounds) return
    event.preventDefault()
    event.currentTarget.setPointerCapture?.(event.pointerId)
    transformSessionRef.current = {
      mode: 'resize',
      pane,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      bounds,
    }
    pinPanes()
    setFrontPane(pane)
    setTransformMode('resize')
  }, [paneBounds, pinPanes, transformable])

  const moveWithKeyboard = useCallback((pane: Pane, event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Home') {
      event.preventDefault()
      event.stopPropagation()
      resetPane(pane)
      return
    }
    const delta = arrowDelta(event)
    const frame = paneFrame(pane)
    if (!delta || !frame) return
    event.preventDefault()
    event.stopPropagation()
    pinPanes()
    setPanePositions((positions) => ({
      ...positions,
      [pane]: clampPosition({ left: frame.left + delta.dx, top: frame.top + delta.dy }, frame),
    }))
    setFrontPane(pane)
  }, [paneFrame, pinPanes, resetPane])

  const resizeWithKeyboard = useCallback((pane: Pane, event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Home') {
      event.preventDefault()
      event.stopPropagation()
      setPaneSizes((sizes) => ({ ...sizes, [pane]: undefined }))
      return
    }
    const delta = arrowDelta(event)
    const bounds = paneBounds(pane)
    if (!delta || !bounds) return
    event.preventDefault()
    event.stopPropagation()
    pinPanes()
    setPaneSizes((sizes) => ({
      ...sizes,
      [pane]: clampSize({ width: bounds.size.width + delta.dx, height: bounds.size.height + delta.dy }, bounds),
    }))
    setFrontPane(pane)
  }, [paneBounds, pinPanes])

  useEffect(() => {
    if (!transformable) return

    const handlePointerMove = (event: PointerEvent) => {
      const session = transformSessionRef.current
      if (!session || event.pointerId !== session.pointerId) return
      const dx = event.clientX - session.startX
      const dy = event.clientY - session.startY
      if (session.mode === 'move') {
        const { pane, frame } = session
        setPanePositions((positions) => ({
          ...positions,
          [pane]: clampPosition({ left: frame.left + dx, top: frame.top + dy }, frame),
        }))
        return
      }
      const { pane, bounds } = session
      setPaneSizes((sizes) => ({
        ...sizes,
        [pane]: clampSize({ width: bounds.size.width + dx, height: bounds.size.height + dy }, bounds),
      }))
    }
    const finishTransform = (event: PointerEvent) => {
      if (event.pointerId !== transformSessionRef.current?.pointerId) return
      transformSessionRef.current = null
      setTransformMode(null)
    }

    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', finishTransform)
    window.addEventListener('pointercancel', finishTransform)
    return () => {
      transformSessionRef.current = null
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', finishTransform)
      window.removeEventListener('pointercancel', finishTransform)
    }
  }, [transformable])

  useEffect(() => {
    if (!transformable) return
    // A smaller window shrinks resized cards to fit and keeps every card in view.
    const keepCardsVisible = () => {
      if (window.innerWidth <= TRANSFORM_BREAKPOINT) {
        resetTransform()
        return
      }
      const available = {
        width: Math.max(1, window.innerWidth - VIEWPORT_GAP * 2),
        height: Math.max(1, window.innerHeight - VIEWPORT_GAP * 2),
      }
      const frames = { main: paneFrame('main'), aside: separate ? paneFrame('aside') : null }
      const fit = (size: Size) => ({
        width: Math.min(size.width, available.width),
        height: Math.min(size.height, available.height),
      })
      setPaneSizes((sizes) => {
        const next = { ...sizes }
        for (const pane of ['main', 'aside'] as const) {
          const size = next[pane]
          if (size) next[pane] = fit(size)
        }
        return next
      })
      setPanePositions((positions) => {
        const next = { ...positions }
        for (const pane of ['main', 'aside'] as const) {
          const position = next[pane]
          const frame = frames[pane]
          if (position && frame) next[pane] = clampPosition(position, fit(frame))
        }
        return next
      })
    }
    window.addEventListener('resize', keepCardsVisible)
    return () => window.removeEventListener('resize', keepCardsVisible)
  }, [paneFrame, resetTransform, separate, transformable])

  useEffect(() => {
    resetTransform()
    transformSessionRef.current = null
    setTransformMode(null)
  }, [activeStepId, refreshKey, resetTransform])

  return {
    panePositions,
    paneSizes,
    frontPane,
    setFrontPane,
    transformMode,
    transformed,
    resetTransform,
    beginMove,
    beginResize,
    moveWithKeyboard,
    resizeWithKeyboard,
  }
}

export type WorkspaceTourTransform = ReturnType<typeof useWorkspaceTourTransform>
