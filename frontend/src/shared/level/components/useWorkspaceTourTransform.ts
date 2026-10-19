import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  KeyboardEvent as ReactKeyboardEvent,
  PointerEvent as ReactPointerEvent,
} from 'react'

import { usePersistentState } from '@/shared/utils/persistentState'

import { VIEWPORT_GAP, type RectSnapshot } from './gameplayWorkspaceTourLayout'
import type {
  WorkspaceTourPane as Pane,
  WorkspaceTourPosition as Position,
  WorkspaceTourSize as Size,
} from './gameplayWorkspaceTourTypes'
import {
  EMPTY_TRANSFORM,
  sanitizeTransformPreference,
  type TransformPreference,
} from './workspaceTourTransformPreference'

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
  transformPreferenceKey,
  activeStepId,
  refreshKey,
}: {
  cardElement: HTMLElement | null
  separate: boolean
  transformable: boolean
  transformPreferenceKey?: string
  activeStepId?: string
  refreshKey?: string | number
}) {
  const [preference, setPreference] = usePersistentState<TransformPreference>(
    transformPreferenceKey ?? null,
    EMPTY_TRANSFORM,
    sanitizeTransformPreference,
  )
  const { panePositions, paneSizes } = preference
  const [frontPane, setFrontPane] = useState<Pane>('main')
  const [transformMode, setTransformMode] = useState<TransformMode | null>(null)
  const [transformViewportEnabled, setTransformViewportEnabled] = useState(
    () => typeof window !== 'undefined' && window.innerWidth > TRANSFORM_BREAKPOINT,
  )
  const transformSessionRef = useRef<TransformSession | null>(null)
  const transformed = transformViewportEnabled && (
    Boolean(panePositions.main || paneSizes.main)
    || (separate && Boolean(panePositions.aside || paneSizes.aside))
  )

  const resetTransform = useCallback(() => {
    setPreference(EMPTY_TRANSFORM)
  }, [setPreference])

  const resetPane = useCallback((pane: Pane) => {
    setPreference((current) => ({
      panePositions: { ...current.panePositions, [pane]: undefined },
      paneSizes: { ...current.paneSizes, [pane]: undefined },
    }))
  }, [setPreference])

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
    setPreference((current) => ({
      ...current,
      panePositions: { ...pinned, ...current.panePositions },
    }))
  }, [paneFrame, separate, setPreference])

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
    setPreference((current) => ({
      ...current,
      panePositions: { ...current.panePositions, [pane]: clampPosition(frame, frame) },
    }))
    setFrontPane(pane)
    setTransformMode('move')
  }, [paneFrame, pinPanes, setPreference, transformable])

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
    setPreference((current) => ({
      ...current,
      panePositions: {
        ...current.panePositions,
        [pane]: clampPosition({ left: frame.left + delta.dx, top: frame.top + delta.dy }, frame),
      },
    }))
    setFrontPane(pane)
  }, [paneFrame, pinPanes, resetPane, setPreference])

  const resizeWithKeyboard = useCallback((pane: Pane, event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Home') {
      event.preventDefault()
      event.stopPropagation()
      setPreference((current) => ({
        ...current,
        paneSizes: { ...current.paneSizes, [pane]: undefined },
      }))
      return
    }
    const delta = arrowDelta(event)
    const bounds = paneBounds(pane)
    if (!delta || !bounds) return
    event.preventDefault()
    event.stopPropagation()
    pinPanes()
    setPreference((current) => ({
      ...current,
      paneSizes: {
        ...current.paneSizes,
        [pane]: clampSize({ width: bounds.size.width + delta.dx, height: bounds.size.height + delta.dy }, bounds),
      },
    }))
    setFrontPane(pane)
  }, [paneBounds, pinPanes, setPreference])

  useEffect(() => {
    if (!transformable) return

    const handlePointerMove = (event: PointerEvent) => {
      const session = transformSessionRef.current
      if (!session || event.pointerId !== session.pointerId) return
      const dx = event.clientX - session.startX
      const dy = event.clientY - session.startY
      if (session.mode === 'move') {
        const { pane, frame } = session
        setPreference((current) => ({
          ...current,
          panePositions: {
            ...current.panePositions,
            [pane]: clampPosition({ left: frame.left + dx, top: frame.top + dy }, frame),
          },
        }))
        return
      }
      const { pane, bounds } = session
      setPreference((current) => ({
        ...current,
        paneSizes: {
          ...current.paneSizes,
          [pane]: clampSize({ width: bounds.size.width + dx, height: bounds.size.height + dy }, bounds),
        },
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
  }, [setPreference, transformable])

  useEffect(() => {
    if (!transformable) return
    // A smaller window shrinks resized cards to fit and keeps every card in view.
    const keepCardsVisible = () => {
      const enabled = window.innerWidth > TRANSFORM_BREAKPOINT
      setTransformViewportEnabled(enabled)
      // Keep the desktop preference intact while a narrow layout temporarily
      // uses the guide's normal responsive placement.
      if (window.innerWidth <= TRANSFORM_BREAKPOINT) {
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
      setPreference((current) => {
        const paneSizesNext = { ...current.paneSizes }
        const panePositionsNext = { ...current.panePositions }
        let changed = false
        for (const pane of ['main', 'aside'] as const) {
          const size = paneSizesNext[pane]
          if (size) {
            const nextSize = fit(size)
            if (nextSize.width !== size.width || nextSize.height !== size.height) {
              paneSizesNext[pane] = nextSize
              changed = true
            }
          }
        }
        for (const pane of ['main', 'aside'] as const) {
          const position = panePositionsNext[pane]
          const frame = frames[pane]
          if (position && frame) {
            const nextPosition = clampPosition(position, fit(frame))
            if (nextPosition.left !== position.left || nextPosition.top !== position.top) {
              panePositionsNext[pane] = nextPosition
              changed = true
            }
          }
        }
        return changed
          ? { panePositions: panePositionsNext, paneSizes: paneSizesNext }
          : current
      })
    }
    keepCardsVisible()
    window.addEventListener('resize', keepCardsVisible)
    return () => window.removeEventListener('resize', keepCardsVisible)
  }, [paneFrame, separate, setPreference, transformable])

  useEffect(() => {
    if (transformPreferenceKey) return
    resetTransform()
    transformSessionRef.current = null
    setTransformMode(null)
  }, [activeStepId, refreshKey, resetTransform, transformPreferenceKey])

  const visiblePanePositions = transformViewportEnabled ? panePositions : {}
  const visiblePaneSizes = transformViewportEnabled ? paneSizes : {}

  return {
    panePositions: visiblePanePositions,
    paneSizes: visiblePaneSizes,
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
