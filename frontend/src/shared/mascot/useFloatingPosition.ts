import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent, PointerEvent } from 'react'

import { readPreference, writePreference } from '@/shared/utils/persistentState'

type Position = { x: number; y: number }

// Matches .mascot-launcher in mascot-launcher.css.
const FLOATING_LAUNCHER_SIZE = { width: 76, height: 104 }
const GAP = 12
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

function keepInView({ x, y }: Position): Position {
  return {
    x: Math.max(GAP, Math.min(window.innerWidth - FLOATING_LAUNCHER_SIZE.width - GAP, x)),
    y: Math.max(TOP, Math.min(window.innerHeight - FLOATING_LAUNCHER_SIZE.height - GAP, y)),
  }
}

function homePosition(): Position {
  return keepInView({ x: window.innerWidth - FLOATING_LAUNCHER_SIZE.width - 24, y: window.innerHeight * 0.42 })
}

// Saved as fractions of the viewport, so a launcher keeps its spot in a resized window.
function savedPosition(key: string): Position {
  const saved = readPreference<Partial<Position> | null>(key, null)
  return saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)
    ? keepInView({ x: saved.x! * window.innerWidth, y: saved.y! * window.innerHeight })
    : homePosition()
}

function savePosition(key: string, { x, y }: Position) {
  writePreference(key, { x: x / window.innerWidth, y: y / window.innerHeight })
}

/**
 * A control the learner can drag anywhere in the viewport, or move with the
 * arrow keys (Home puts it back). Its position is remembered under `key`.
 */
export function useFloatingPosition(key: string, onDragStart?: () => void) {
  const [position, setPosition] = useState(() => savedPosition(key))
  const [dragging, setDragging] = useState(false)
  const latest = useRef(position)
  const press = useRef<{ id: number; start: Position; origin: Position; moved: boolean } | null>(null)
  // Set when a press ends as a drag, so the click that follows does not open anything.
  const dragged = useRef(false)

  function place(next: Position) {
    latest.current = keepInView(next)
    setPosition(latest.current)
  }

  useEffect(() => {
    const fit = () => {
      latest.current = keepInView(latest.current)
      setPosition(latest.current)
    }
    window.addEventListener('resize', fit)
    return () => window.removeEventListener('resize', fit)
  }, [])

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
        : homePosition())
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
