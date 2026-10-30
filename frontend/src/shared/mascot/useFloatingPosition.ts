import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent, PointerEvent } from 'react'

import { readPreference, writePreference } from '@/shared/utils/persistentState'

type Position = { x: number; y: number }
export type FloatingSize = { width: number; height: number }
export type FloatingHomeSlot = 'upper' | 'lower'

// Matches .mascot-launcher (and its [data-size="large"] variant) in mascot-launcher.css.
export const FLOATING_LAUNCHER_SIZES = {
  default: { width: 76, height: 104 },
  large: { width: 128, height: 180 },
} satisfies Record<string, FloatingSize>
const GAP = 12
const LAUNCHER_GAP = 24
// Below the app's top bar.
const TOP = 64
// A press that travels less than this is a click, not a drag.
const DRAG_THRESHOLD = 6
const KEY_STEP = 10
const KEY_STEP_LARGE = 40
const ARROWS: Record<string, Position> = {
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
}

function keepInView({ x, y }: Position, size: FloatingSize): Position {
  return {
    x: Math.max(GAP, Math.min(window.innerWidth - size.width - GAP, x)),
    y: Math.max(TOP, Math.min(window.innerHeight - size.height - GAP, y)),
  }
}

function homePosition(size: FloatingSize, slot?: FloatingHomeSlot): Position {
  let y = window.innerHeight * 0.42
  if (slot) {
    // Reserve both launchers' height so their gap survives shorter viewports.
    const stackHeight = size.height * 2 + LAUNCHER_GAP
    y = Math.max(TOP, Math.min(y, window.innerHeight - stackHeight - GAP))
    if (slot === 'lower') y += size.height + LAUNCHER_GAP
  }
  return keepInView({ x: window.innerWidth - size.width - 24, y }, size)
}

// Saved as fractions of the viewport, so a launcher keeps its spot in a resized window.
function savedPosition(key: string, size: FloatingSize, slot?: FloatingHomeSlot): Position {
  const saved = readPreference<Partial<Position> | null>(key, null)
  return saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)
    ? keepInView({ x: saved.x! * window.innerWidth, y: saved.y! * window.innerHeight }, size)
    : homePosition(size, slot)
}

// Where each launcher last stood while visible, so another can take its place:
// the workspace's guide mascot becomes a finished run's next-step mascot.
type ShownLauncher = { position: Position; size: FloatingSize; order: number }
const lastShown = new Map<string, ShownLauncher>()
let shownOrder = 0

export function rememberShownPosition(key: string, position: Position, size: FloatingSize) {
  lastShown.set(key, { position, size, order: ++shownOrder })
}

/** Stands a launcher of `size` where the most recently visible of `keys` stood, feet aligned. */
function handoffPosition(keys: readonly string[], size: FloatingSize): Position | null {
  let latest: ShownLauncher | undefined
  for (const key of keys) {
    const shown = lastShown.get(key)
    if (shown && (!latest || shown.order > latest.order)) latest = shown
  }
  if (!latest) return null
  return keepInView({
    x: latest.position.x + latest.size.width / 2 - size.width / 2,
    y: latest.position.y + latest.size.height - size.height,
  }, size)
}

function savePosition(key: string, { x, y }: Position) {
  writePreference(key, { x: x / window.innerWidth, y: y / window.innerHeight })
}

/**
 * A control the learner can drag anywhere in the viewport, or move with the
 * arrow keys (Home puts it back). Its position is remembered under `key`.
 */
export function useFloatingPosition(
  key: string,
  onDragStart?: () => void,
  size: FloatingSize = FLOATING_LAUNCHER_SIZES.default,
  /** Keys of launchers this one replaces; it starts where the latest of them was last seen. */
  takeOverFrom: readonly string[] = [],
  homeSlot?: FloatingHomeSlot,
) {
  const [position, setPosition] = useState(() => handoffPosition(takeOverFrom, size) ?? savedPosition(key, size, homeSlot))
  const [dragging, setDragging] = useState(false)
  const latest = useRef(position)
  const press = useRef<{ id: number; start: Position; origin: Position; moved: boolean } | null>(null)
  // Set when a press ends as a drag, so the click that follows does not open anything.
  const dragged = useRef(false)

  function place(next: Position) {
    latest.current = keepInView(next, size)
    setPosition(latest.current)
  }

  useEffect(() => {
    let home = homePosition(size, homeSlot)
    const fit = () => {
      const nextHome = homePosition(size, homeSlot)
      const atHome = homeSlot && latest.current.x === home.x && latest.current.y === home.y
      latest.current = atHome ? nextHome : keepInView(latest.current, size)
      home = nextHome
      setPosition(latest.current)
    }
    window.addEventListener('resize', fit)
    return () => window.removeEventListener('resize', fit)
  }, [homeSlot, size])

  const handlers = {
    onPointerDown(event: PointerEvent<HTMLElement>) {
      if (event.button !== 0) return
      dragged.current = false
      press.current = { id: event.pointerId, start: { x: event.clientX, y: event.clientY }, origin: latest.current, moved: false }
      event.currentTarget.setPointerCapture?.(event.pointerId)
    },
    onPointerMove(event: PointerEvent<HTMLElement>) {
      const current = press.current
      if (!current || current.id !== event.pointerId) return
      const dx = event.clientX - current.start.x
      const dy = event.clientY - current.start.y
      if (!current.moved) {
        if (Math.hypot(dx, dy) < DRAG_THRESHOLD) return
        current.moved = true
        setDragging(true)
        onDragStart?.()
      }
      place({ x: current.origin.x + dx, y: current.origin.y + dy })
    },
    onPointerUp(event: PointerEvent<HTMLElement>) {
      const current = press.current
      if (!current || current.id !== event.pointerId) return
      press.current = null
      dragged.current = current.moved
      if (current.moved) savePosition(key, latest.current)
      setDragging(false)
    },
    onPointerCancel() {
      press.current = null
      dragged.current = false
      setDragging(false)
    },
    onKeyDown(event: KeyboardEvent<HTMLElement>) {
      if (event.key === 'Enter' || event.key === ' ') {
        dragged.current = false
        return
      }
      const arrow = ARROWS[event.key]
      if (!arrow && event.key !== 'Home') return
      event.preventDefault()
      event.stopPropagation()
      const step = event.shiftKey ? KEY_STEP_LARGE : KEY_STEP
      place(arrow
        ? { x: latest.current.x + arrow.x * step, y: latest.current.y + arrow.y * step }
        : homePosition(size, homeSlot))
      savePosition(key, latest.current)
    },
  }

  /** Whether the click that just happened was a click rather than the end of a drag. */
  function clicked() {
    const wasDrag = dragged.current
    dragged.current = false
    return !wasDrag
  }

  return { position, dragging, handlers, clicked }
}
