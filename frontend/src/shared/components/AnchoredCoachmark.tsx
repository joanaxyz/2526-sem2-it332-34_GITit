import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

type Position = { top: number; left: number; caretSide: 'bottom' | 'top' | 'right' | 'left'; caretOffset: number }

function computePosition(target: DOMRect, popup: { w: number; h: number }): Position {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const gap = 12
  const pad = 10

  // Prefer above the target
  if (target.top - popup.h - gap > pad) {
    const left = Math.min(Math.max(pad, target.left + target.width / 2 - popup.w / 2), vw - popup.w - pad)
    const caretOffset = Math.max(16, Math.min(popup.w - 28, target.left + target.width / 2 - left))
    return { top: target.top - popup.h - gap, left, caretSide: 'bottom', caretOffset }
  }
  // Below the target
  if (target.bottom + popup.h + gap < vh - pad) {
    const left = Math.min(Math.max(pad, target.left + target.width / 2 - popup.w / 2), vw - popup.w - pad)
    const caretOffset = Math.max(16, Math.min(popup.w - 28, target.left + target.width / 2 - left))
    return { top: target.bottom + gap, left, caretSide: 'top', caretOffset }
  }
  // Left of the target
  if (target.left - popup.w - gap > pad) {
    const top = Math.min(Math.max(pad, target.top + target.height / 2 - popup.h / 2), vh - popup.h - pad)
    const caretOffset = Math.max(16, Math.min(popup.h - 28, target.top + target.height / 2 - top))
    return { top, left: target.left - popup.w - gap, caretSide: 'right', caretOffset }
  }
  // Right of the target (fallback)
  const top = Math.min(Math.max(pad, target.top + target.height / 2 - popup.h / 2), vh - popup.h - pad)
  const caretOffset = Math.max(16, Math.min(popup.h - 28, target.top + target.height / 2 - top))
  return { top, left: target.right + gap, caretSide: 'left', caretOffset }
}

function posEqual(a: Position | null, b: Position): boolean {
  return (
    a !== null &&
    a.top === b.top &&
    a.left === b.left &&
    a.caretSide === b.caretSide &&
    a.caretOffset === b.caretOffset
  )
}

export function AnchoredCoachmark({
  targetSelector,
  title,
  body,
  dismissLabel = 'Got it',
  onDismiss,
}: {
  targetSelector: string
  title: string
  body: string
  dismissLabel?: string
  onDismiss: () => void
}) {
  const popupRef = useRef<HTMLDivElement>(null)
  const [pos, setPos] = useState<Position | null>(null)

  function reposition() {
    const target = document.querySelector(targetSelector)
    const popup = popupRef.current
    if (!target || !popup) return
    const rect = target.getBoundingClientRect()
    if (rect.width === 0 && rect.height === 0) return
    const next = computePosition(rect, { w: popup.offsetWidth, h: popup.offsetHeight })
    // Only update state when position actually changes to avoid infinite loops
    setPos((prev) => (posEqual(prev, next) ? prev : next))
  }

  // Run once after mount to measure and position, then only on resize/scroll
  useLayoutEffect(() => {
    reposition()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetSelector])

  useEffect(() => {
    window.addEventListener('resize', reposition)
    window.addEventListener('scroll', reposition, true)
    return () => {
      window.removeEventListener('resize', reposition)
      window.removeEventListener('scroll', reposition, true)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetSelector])

  const style: React.CSSProperties = pos
    ? { position: 'fixed', top: pos.top, left: pos.left, visibility: 'visible' }
    : { position: 'fixed', top: -9999, left: -9999, visibility: 'hidden' }

  return createPortal(
    <div
      ref={popupRef}
      className="anchored-coachmark"
      data-caret={pos?.caretSide ?? 'bottom'}
      style={{ ...style, '--caret-offset': `${pos?.caretOffset ?? 20}px` } as React.CSSProperties}
      role="status"
      aria-live="polite"
    >
      <p className="anchored-coachmark__title">{title}</p>
      <p className="anchored-coachmark__body">{body}</p>
      <button type="button" className="anchored-coachmark__dismiss" onClick={onDismiss}>
        {dismissLabel}
      </button>
    </div>,
    document.body,
  )
}
