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
} from './gameplayWorkspaceTourTypes'
import {
  PANE_MINIMUMS,
  SOUTH_EAST,
  TRANSFORM_BREAKPOINT,
  arrowDelta,
  clampPosition,
  clampSize,
  edgesAt,
  fitTransformToViewport,
  onScrollbar,
  resizeCursor,
  resizeFrame,
  workspaceTourFrame,
  type Edges,
  type PaneBounds,
  type TransformMode,
} from './workspaceTourGeometry'
import {
  EMPTY_TRANSFORM,
  sanitizeTransformPreference,
  type TransformPreference,
} from './workspaceTourTransformPreference'

type TransformSession = {
  mode: TransformMode
  pane: Pane
  pointerId: number
  startX: number
  startY: number
  frame: RectSnapshot
  edges: Edges
  cursor: string
  /** Every card's spot when the drag began, pinned once the drag really starts. */
  pinned: Partial<Record<Pane, Position>>
  /** False until the pointer travels past the drag threshold, so a click stays a click. */
  started: boolean
}

const DRAG_THRESHOLD = 3
// The visible card inside a pane: the guide's speech bubble when there is one.
const PANE_SURFACE = '.mascot-message__bubble'
// Pressing these does their own thing (click, select a command) instead of moving the card.
const NO_DRAG = 'button, a, input, textarea, select, label, [role="tab"], [contenteditable="true"], code, pre, kbd'

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
  const [transformCursor, setTransformCursor] = useState<string | null>(null)
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

  const pinnedPositions = useCallback(() => {
    const pinned: Partial<Record<Pane, Position>> = {}
    for (const pane of separate ? ['main', 'aside'] as const : ['main'] as const) {
      const frame = paneFrame(pane)
      if (frame) pinned[pane] = { left: frame.left, top: frame.top }
    }
    return pinned
  }, [paneFrame, separate])

  /** The first transform pins every card so only the active card then changes. */
  const pinPanes = useCallback(() => {
    const pinned = pinnedPositions()
    setPreference((current) => ({
      ...current,
      panePositions: { ...pinned, ...current.panePositions },
    }))
  }, [pinnedPositions, setPreference])

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

  const beginTransform = useCallback((
    pane: Pane,
    event: ReactPointerEvent<HTMLElement>,
    mode: TransformMode,
    edges: Edges = SOUTH_EAST,
  ) => {
    if (!transformable || window.innerWidth <= TRANSFORM_BREAKPOINT) return
    const frame = paneFrame(pane)
    if (!frame) return
    event.preventDefault()
    event.currentTarget.setPointerCapture?.(event.pointerId)
    transformSessionRef.current = {
      mode,
      pane,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      frame,
      edges,
      cursor: mode === 'move' ? 'grabbing' : resizeCursor(edges),
      pinned: pinnedPositions(),
      started: false,
    }
  }, [paneFrame, pinnedPositions, transformable])

  const beginMove = useCallback((pane: Pane, event: ReactPointerEvent<HTMLElement>) => {
    beginTransform(pane, event, 'move')
  }, [beginTransform])

  const beginResize = useCallback((pane: Pane, event: ReactPointerEvent<HTMLElement>) => {
    beginTransform(pane, event, 'resize')
  }, [beginTransform])

  const paneEdgesAt = useCallback((pane: Pane, event: ReactPointerEvent<HTMLElement>) => {
    const element = paneElement(pane)
    const surface = element?.querySelector<HTMLElement>(PANE_SURFACE) ?? element
    return surface ? edgesAt(surface.getBoundingClientRect(), event.clientX, event.clientY) : null
  }, [paneElement])

  /**
   * With a mouse the card itself is the grip: its edges resize it and the rest
   * moves it. Touch keeps the grip and resize buttons, so a swipe still scrolls.
   */
  const pointerDownOnPane = useCallback((pane: Pane, event: ReactPointerEvent<HTMLElement>) => {
    if (event.defaultPrevented || event.pointerType !== 'mouse' || event.button !== 0) return
    const edges = paneEdgesAt(pane, event)
    if (edges) {
      beginTransform(pane, event, 'resize', edges)
      return
    }
    if ((event.target as Element).closest(NO_DRAG) || onScrollbar(event)) return
    beginTransform(pane, event, 'move')
  }, [beginTransform, paneEdgesAt])

  /** A mouse at a card's edge shows the resize cursor for that edge. */
  const hoverPane = useCallback((pane: Pane, event: ReactPointerEvent<HTMLElement>) => {
    if (event.pointerType !== 'mouse' || transformSessionRef.current?.started) return
    const enabled = transformable && window.innerWidth > TRANSFORM_BREAKPOINT
    const edges = enabled ? paneEdgesAt(pane, event) : null
    if (edges) event.currentTarget.dataset.resizeCursor = resizeCursor(edges)
    else delete event.currentTarget.dataset.resizeCursor
  }, [paneEdgesAt, transformable])

  const leavePane = useCallback((event: ReactPointerEvent<HTMLElement>) => {
    delete event.currentTarget.dataset.resizeCursor
  }, [])

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
      if (!session.started) {
        if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return
        session.started = true
        setFrontPane(session.pane)
        setTransformMode(session.mode)
        setTransformCursor(session.cursor)
      }
      const { pane, frame, pinned } = session
      if (session.mode === 'move') {
        setPreference((current) => ({
          ...current,
          panePositions: {
            ...pinned,
            ...current.panePositions,
            [pane]: clampPosition({ left: frame.left + dx, top: frame.top + dy }, frame),
          },
        }))
        return
      }
      const { position, size } = resizeFrame(frame, session.edges, dx, dy, PANE_MINIMUMS[pane])
      setPreference((current) => ({
        panePositions: { ...pinned, ...current.panePositions, [pane]: position },
        paneSizes: { ...current.paneSizes, [pane]: size },
      }))
    }
    const finishTransform = (event: PointerEvent) => {
      if (event.pointerId !== transformSessionRef.current?.pointerId) return
      transformSessionRef.current = null
      setTransformMode(null)
      setTransformCursor(null)
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
      const frames = { main: paneFrame('main'), aside: separate ? paneFrame('aside') : null }
      setPreference((current) => fitTransformToViewport(current, frames))
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
    setTransformCursor(null)
  }, [activeStepId, refreshKey, resetTransform, transformPreferenceKey])

  const visiblePanePositions = transformViewportEnabled ? panePositions : {}
  const visiblePaneSizes = transformViewportEnabled ? paneSizes : {}

  return {
    panePositions: visiblePanePositions,
    paneSizes: visiblePaneSizes,
    frontPane,
    setFrontPane,
    transformMode,
    transformCursor,
    transformed,
    resetTransform,
    beginMove,
    beginResize,
    pointerDownOnPane,
    hoverPane,
    leavePane,
    moveWithKeyboard,
    resizeWithKeyboard,
  }
}

export type WorkspaceTourTransform = ReturnType<typeof useWorkspaceTourTransform>
