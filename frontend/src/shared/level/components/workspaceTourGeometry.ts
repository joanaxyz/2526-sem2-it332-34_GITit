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
import type { TransformPreference } from './workspaceTourTransformPreference'

export type PaneBounds = { size: Size; minimum: Size; maximum: Size }

export type TransformMode = 'move' | 'resize'

/** The card edges a resize drags; a corner drags two. */
export type Edges = { left: boolean; right: boolean; top: boolean; bottom: boolean }

export const TRANSFORM_BREAKPOINT = 600
export const PANE_MINIMUMS: Record<Pane, Size> = {
  main: { width: 304, height: 220 },
  aside: { width: 240, height: 160 },
}
const KEYBOARD_TRANSFORM_STEP = 16
// How close to a card's edge a mouse grabs that edge instead of moving the card.
const EDGE_ZONE = 8
export const SOUTH_EAST: Edges = { left: false, right: true, top: false, bottom: true }

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

export function clampPosition(position: Position, size: Size): Position {
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

export function clampSize(size: Size, { minimum, maximum }: PaneBounds): Size {
  return {
    width: clamp(size.width, minimum.width, maximum.width),
    height: clamp(size.height, minimum.height, maximum.height),
  }
}

/** The dragged edges follow the pointer; the opposite edges stay put. */
export function resizeFrame(frame: RectSnapshot, edges: Edges, dx: number, dy: number, minimum: Size) {
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
export function edgesAt(rect: DOMRect, x: number, y: number): Edges | null {
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) return null
  const edges = {
    left: x - rect.left < EDGE_ZONE,
    right: rect.right - x < EDGE_ZONE,
    top: y - rect.top < EDGE_ZONE,
    bottom: rect.bottom - y < EDGE_ZONE,
  }
  return edges.left || edges.right || edges.top || edges.bottom ? edges : null
}

export function resizeCursor({ left, right, top, bottom }: Edges) {
  if ((left && top) || (right && bottom)) return 'nwse-resize'
  if ((right && top) || (left && bottom)) return 'nesw-resize'
  return left || right ? 'ew-resize' : 'ns-resize'
}

/** A press on a scroll area's own scrollbar, which scrolls rather than moves the card. */
export function onScrollbar(event: ReactPointerEvent<HTMLElement>) {
  const target = event.target as HTMLElement
  const { offsetX, offsetY } = event.nativeEvent
  return target.clientWidth > 0 && (offsetX > target.clientWidth || offsetY > target.clientHeight)
}

/** Shrinks resized cards to the viewport and keeps every pinned card in view. */
export function fitTransformToViewport(
  current: TransformPreference,
  frames: Record<Pane, RectSnapshot | null>,
): TransformPreference {
  const available = {
    width: Math.max(1, window.innerWidth - VIEWPORT_GAP * 2),
    height: Math.max(1, window.innerHeight - VIEWPORT_GAP * 2),
  }
  const fit = (size: Size) => ({
    width: Math.min(size.width, available.width),
    height: Math.min(size.height, available.height),
  })
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
}

/** Arrow keys as a step, farther with Shift; null for any other key. */
export function arrowDelta(event: ReactKeyboardEvent) {
  const step = event.shiftKey ? KEYBOARD_TRANSFORM_STEP * 3 : KEYBOARD_TRANSFORM_STEP
  switch (event.key) {
    case 'ArrowLeft': return { dx: -step, dy: 0 }
    case 'ArrowRight': return { dx: step, dy: 0 }
    case 'ArrowUp': return { dx: 0, dy: -step }
    case 'ArrowDown': return { dx: 0, dy: step }
    default: return null
  }
}
