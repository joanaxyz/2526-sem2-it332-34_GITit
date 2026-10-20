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

/** The card edges a resize drags; a corner drags two. */
type Edges = { left: boolean; right: boolean; top: boolean; bottom: boolean }

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

const TRANSFORM_BREAKPOINT = 600
const PANE_MINIMUMS: Record<Pane, Size> = {
  main: { width: 304, height: 220 },
  aside: { width: 240, height: 160 },
}
const KEYBOARD_TRANSFORM_STEP = 16
const DRAG_THRESHOLD = 3
// How close to a card's edge a mouse grabs that edge instead of moving the card.
const EDGE_ZONE = 8
const SOUTH_EAST: Edges = { left: false, right: true, top: false, bottom: true }
// The visible card inside a pane: the guide's speech bubble when there is one.
const PANE_SURFACE = '.mascot-message__bubble'
// Pressing these does their own thing (click, select a command) instead of moving the card.
const NO_DRAG = 'button, a, input, textarea, select, label, [role="tab"], [contenteditable="true"], code, pre, kbd'

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

function clamp(value: number, low: number, high: number) {
  return Math.min(Math.max(value, Math.min(low, high)), high)
}

function clampSize(size: Size, { minimum, maximum }: PaneBounds): Size {
  return {
    width: clamp(size.width, minimum.width, maximum.width),
    height: clamp(size.height, minimum.height, maximum.height),
  }
}

/** The dragged edges follow the pointer; the opposite edges stay put. */
function resizeFrame(frame: RectSnapshot, edges: Edges, dx: number, dy: number, minimum: Size) {
  let { left, top, width, height } = frame
  if (edges.right) width = clamp(frame.width + dx, minimum.width, window.innerWidth - VIEWPORT_GAP - frame.left)
  if (edges.bottom) height = clamp(frame.height + dy, minimum.height, window.innerHeight - VIEWPORT_GAP - frame.top)
  if (edges.left) {
    left = Math.max(VIEWPORT_GAP, Math.min(frame.left + dx, frame.right - minimum.width))
    width = frame.right - left
  }
  if (edges.top) {
    top = Math.max(VIEWPORT_GAP, Math.min(frame.top + dy, frame.bottom - minimum.height))
    height = frame.bottom - top
  }
  return { position: { left, top }, size: { width, height } }
}

/** The edges of `rect` the pointer is on; null away from the edges or outside. */
function edgesAt(rect: DOMRect, x: number, y: number): Edges | null {
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) return null
  const edges = {
    left: x - rect.left < EDGE_ZONE,
    right: rect.right - x < EDGE_ZONE,
    top: y - rect.top < EDGE_ZONE,
    bottom: rect.bottom - y < EDGE_ZONE,
  }
  return edges.left || edges.right || edges.top || edges.bottom ? edges : null
}

function resizeCursor({ left, right, top, bottom }: Edges) {
  if ((left && top) || (right && bottom)) return 'nwse-resize'
  if ((right && top) || (left && bottom)) return 'nesw-resize'
  return left || right ? 'ew-resize' : 'ns-resize'
}

/** A press on a scroll area's own scrollbar, which scrolls rather than moves the card. */
function onScrollbar(event: ReactPointerEvent<HTMLElement>) {
  const target = event.target as HTMLElement
  const { offsetX, offsetY } = event.nativeEvent
  return target.clientWidth > 0 && (offsetX > target.clientWidth || offsetY > target.clientHeight)
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
