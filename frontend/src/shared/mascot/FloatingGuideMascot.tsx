import { type ReactNode, type Ref, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { GuideCharacterPortrait } from './GuideCharacterPortrait'
import { useGuideMascotVisibility } from './useGuideMascotVisibility'
import './guide-launcher.css'

const POSITION_KEY = 'git-it:guide-mascot-position:v1'
const WIDTH = 76
const HEIGHT = 104
const GAP = 12
type Position = { x: number; y: number }

function clamp(position: Position): Position {
  return {
    x: Math.max(GAP, Math.min(window.innerWidth - WIDTH - GAP, position.x)),
    y: Math.max(64, Math.min(window.innerHeight - HEIGHT - GAP, position.y)),
  }
}
function initialPosition(): Position {
  try {
    const saved = JSON.parse(localStorage.getItem(POSITION_KEY) ?? 'null')
    if (saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)) {
      return clamp({ x: saved.x * window.innerWidth, y: saved.y * window.innerHeight })
    }
  } catch { /* The guide remains usable when storage is unavailable. */ }
  return clamp({ x: window.innerWidth - WIDTH - 24, y: window.innerHeight * 0.42 })
}
function remember(position: Position) {
  try {
    localStorage.setItem(POSITION_KEY, JSON.stringify({ x: position.x / window.innerWidth, y: position.y / window.innerHeight }))
  } catch { /* Dragging does not depend on browser storage. */ }
}

/** Click opens the guide; a drag only moves its launcher. */
export function FloatingGuideMascot({ label, active = false, onActivate, buttonRef, onDragStart, children, tourTarget }: {
  label: string
  active?: boolean
  onActivate: () => void
  buttonRef?: Ref<HTMLButtonElement>
  onDragStart?: () => void
  children?: ReactNode
  tourTarget?: string
}) {
  const guideMascotVisible = useGuideMascotVisibility()
  const [position, setPosition] = useState(initialPosition)
  const [dragging, setDragging] = useState(false)
  const positionRef = useRef(position)
  positionRef.current = position
  const drag = useRef<{ id: number; start: Position; origin: Position; moved: boolean } | null>(null)
  const suppressClick = useRef(false)

  useEffect(() => {
    if (!guideMascotVisible) return
    const resize = () => setPosition((current) => clamp(current))
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [guideMascotVisible])

  if (!guideMascotVisible) return null

  return createPortal(<div className="guide-mascot" data-dragging={dragging || undefined}
    aria-hidden={active || undefined} inert={active || undefined}
    style={{ left: position.x, top: position.y }}>
    <button ref={buttonRef} type="button" className={`guide-mascot__button${active ? ' is-active' : ''}`}
      aria-label={label} aria-expanded={active} data-command-guide-launcher data-tour-target={tourTarget}
      title={`${label} · Drag to move. Arrow keys move; Home resets.`}
      onPointerDown={(event) => {
        if (event.button !== 0) return
        suppressClick.current = false
        drag.current = { id: event.pointerId, start: { x: event.clientX, y: event.clientY }, origin: positionRef.current, moved: false }
        event.currentTarget.setPointerCapture?.(event.pointerId)
      }}
      onPointerMove={(event) => {
        const current = drag.current
        if (!current || current.id !== event.pointerId) return
        const dx = event.clientX - current.start.x
        const dy = event.clientY - current.start.y
        if (!current.moved && Math.hypot(dx, dy) < 6) return
        if (!current.moved) { current.moved = true; setDragging(true); onDragStart?.() }
        const next = clamp({ x: current.origin.x + dx, y: current.origin.y + dy })
        positionRef.current = next
        setPosition(next)
      }}
      onPointerUp={(event) => {
        const current = drag.current
        if (!current || current.id !== event.pointerId) return
        suppressClick.current = current.moved
        if (current.moved) remember(positionRef.current)
        drag.current = null
        setDragging(false)
        if (event.currentTarget.hasPointerCapture?.(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
      }}
      onPointerCancel={() => { drag.current = null; suppressClick.current = false; setDragging(false) }}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') { suppressClick.current = false; return }
        const step = event.shiftKey ? 40 : 10
        const offsets: Record<string, Position> = { ArrowLeft: { x: -step, y: 0 }, ArrowRight: { x: step, y: 0 }, ArrowUp: { x: 0, y: -step }, ArrowDown: { x: 0, y: step } }
        if (!offsets[event.key] && event.key !== 'Home') return
        event.preventDefault()
        event.stopPropagation()
        const delta = offsets[event.key]
        const next = event.key === 'Home' ? clamp({ x: window.innerWidth - WIDTH - 24, y: window.innerHeight * 0.42 })
          : clamp({ x: positionRef.current.x + delta.x, y: positionRef.current.y + delta.y })
        positionRef.current = next
        setPosition(next)
        remember(next)
      }}
      onClick={() => {
        if (suppressClick.current) { suppressClick.current = false; return }
        if (!active) onActivate()
      }}>
      <GuideCharacterPortrait className="guide-mascot__portrait" alt="" width={72} height={90} />
      <span>Guide</span>
    </button>
    {children}
  </div>, document.body)
}
