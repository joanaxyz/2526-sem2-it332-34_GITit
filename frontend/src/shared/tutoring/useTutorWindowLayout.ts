import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent, PointerEvent } from 'react'

import { edgesAt, onScrollbar, resizeCursor, SOUTH_EAST, type Edges } from '@/shared/level/components/workspaceTourGeometry'
import { usePersistentState } from '@/shared/utils/persistentState'

type Rect = { x: number; y: number; width: number; height: number }
type Area = { left: number; top: number; right: number; bottom: number }
/** A drag in progress: `edges` resizes from those edges; null moves the window. */
type Drag = { pointerId: number; x: number; y: number; rect: Rect; edges: Edges | null }

const MINIMUM = { width: 320, height: 360 }
const GAP = 12
// Below the app's top bar.
const TOP = 76
// Above Home's mobile navigation bar.
const MOBILE_NAV_GAP = 88
const KEY_STEP = 10
const KEY_STEP_LARGE = 40
const ARROWS: Record<string, [number, number]> = {
  ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1],
}
// Pressing these uses them; it never moves or resizes the window.
const CONTROLS = 'button, a, input, textarea, select, summary, label, [contenteditable]:not([contenteditable="false"]), [data-tutor-selectable]'

function clamp(value: number, low: number, high: number) {
  return Math.max(low, Math.min(value, high))
}

function viewportArea(workspace: boolean): Area {
  const bottomGap = !workspace && window.innerWidth <= 720 ? MOBILE_NAV_GAP : GAP
  return { left: GAP, top: TOP, right: window.innerWidth - GAP, bottom: window.innerHeight - bottomGap }
}

/** The window at its size and place, shrunk if needed, and fully inside the area. */
function fit(rect: Rect, area: Area): Rect {
  const maxWidth = Math.max(240, area.right - area.left)
  const maxHeight = Math.max(180, area.bottom - area.top)
  const width = clamp(rect.width, Math.min(MINIMUM.width, maxWidth), maxWidth)
  const height = clamp(rect.height, Math.min(MINIMUM.height, maxHeight), maxHeight)
  return {
    width,
    height,
    x: clamp(rect.x, area.left, area.right - width),
    y: clamp(rect.y, area.top, area.bottom - height),
  }
}

/** The dragged edges follow the pointer; the opposite edges stay put. */
function resize(rect: Rect, edges: Edges, dx: number, dy: number, area: Area): Rect {
  let left = rect.x
  let top = rect.y
  let right = rect.x + rect.width
  let bottom = rect.y + rect.height
  if (edges.left) left = clamp(left + dx, area.left, right - MINIMUM.width)
  if (edges.right) right = clamp(right + dx, left + MINIMUM.width, area.right)
  if (edges.top) top = clamp(top + dy, area.top, bottom - MINIMUM.height)
  if (edges.bottom) bottom = clamp(bottom + dy, top + MINIMUM.height, area.bottom)
  return fit({ x: left, y: top, width: right - left, height: bottom - top }, area)
}

function move(rect: Rect, dx: number, dy: number, area: Area): Rect {
  return fit({ ...rect, x: rect.x + dx, y: rect.y + dy }, area)
}

function defaultRect(workspace: boolean): Rect {
  if (workspace) {
    // Keep the chat in the lower-right portion of the workspace on smaller laptops too.
    const width = clamp(window.innerWidth * 0.27, MINIMUM.width, 420)
    const height = clamp(window.innerHeight * 0.44, MINIMUM.height, 424)
    return fit({ x: window.innerWidth - width - 52, y: window.innerHeight - height - 38, width, height }, viewportArea(workspace))
  }
  return fit({ x: window.innerWidth - 440, y: window.innerHeight - 680, width: 420, height: 640 }, viewportArea(workspace))
}

function isRect(value: unknown): value is Rect {
  const rect = value as Partial<Rect> | null
  return Boolean(rect) && [rect?.x, rect?.y, rect?.width, rect?.height].every(Number.isFinite)
}

/**
 * Where the chat window sits and how big it is, remembered between openings.
 * Its background and side mascot drag it; a mouse resizes it from any edge.
 * Text, controls and scrollbars retain their native interactions.
 * Keyboard controls move and resize it with the arrow keys.
 */
export function useTutorWindowLayout(workspace: boolean) {
  const [rect, setRect] = usePersistentState<Rect>(
    `tutor-window:${workspace ? 'workspace' : 'home'}`,
    defaultRect(workspace),
    (saved) => (isRect(saved) ? fit(saved, viewportArea(workspace)) : defaultRect(workspace)),
  )
  const [cursor, setCursor] = useState<string | null>(null)
  const drag = useRef<Drag | null>(null)

  useEffect(() => {
    const refit = () => setRect((current) => fit(current, viewportArea(workspace)))
    window.addEventListener('resize', refit)
    return () => window.removeEventListener('resize', refit)
  }, [setRect, workspace])

  /** The window edges under a mouse or pen; touch moves instead of resizing. */
  function edgesUnder(event: PointerEvent<HTMLElement>) {
    if (event.pointerType === 'touch' || (event.target as Element).closest(CONTROLS)) return null
    return edgesAt(event.currentTarget.getBoundingClientRect(), event.clientX, event.clientY)
  }

  function endDrag(event: PointerEvent<HTMLElement>) {
    if (drag.current?.pointerId !== event.pointerId) return
    drag.current = null
    setCursor(null)
    if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
  }

  const frameHandlers = {
    onPointerDown(event: PointerEvent<HTMLElement>) {
      if (event.button !== 0 || (event.target as Element).closest(CONTROLS) || onScrollbar(event)) return
      const edges = edgesUnder(event)
      event.preventDefault()
      event.currentTarget.setPointerCapture?.(event.pointerId)
      drag.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, rect, edges }
      setCursor(edges ? resizeCursor(edges) : 'grabbing')
    },
    onPointerMove(event: PointerEvent<HTMLElement>) {
      const start = drag.current
      if (!start) {
        // The cursor shows which edges a press would resize.
        const edges = edgesUnder(event)
        setCursor(edges ? resizeCursor(edges) : null)
        return
      }
      if (start.pointerId !== event.pointerId) return
      const dx = event.clientX - start.x
      const dy = event.clientY - start.y
      const area = viewportArea(workspace)
      setRect(start.edges ? resize(start.rect, start.edges, dx, dy, area) : move(start.rect, dx, dy, area))
    },
    onPointerUp: endDrag,
    onPointerCancel: endDrag,
    onLostPointerCapture: endDrag,
    onPointerLeave() {
      if (!drag.current) setCursor(null)
    },
  }

  function keyboard(mode: 'move' | 'resize') {
    return (event: KeyboardEvent<HTMLElement>) => {
      const arrow = ARROWS[event.key]
      if (!arrow && event.key !== 'Home') return
      event.preventDefault()
      event.stopPropagation()
      if (!arrow) {
        setRect(defaultRect(workspace))
        return
      }
      const step = event.shiftKey ? KEY_STEP_LARGE : KEY_STEP
      const [dx, dy] = [arrow[0] * step, arrow[1] * step]
      const area = viewportArea(workspace)
      setRect((current) => (mode === 'move' ? move(current, dx, dy, area) : resize(current, SOUTH_EAST, dx, dy, area)))
    }
  }

  return {
    rect,
    /** The cursor while the pointer is on an edge or dragging; null otherwise. */
    cursor,
    frameHandlers,
    moveWithKeyboard: keyboard('move'),
    resizeWithKeyboard: keyboard('resize'),
  }
}
