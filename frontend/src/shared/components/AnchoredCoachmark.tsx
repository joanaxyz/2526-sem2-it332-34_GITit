import { ArrowRight, BookOpen, MessageCircle, X } from 'lucide-react'
import { useId, useLayoutEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

type Position = { top: number; left: number; caretSide: 'bottom' | 'top' | 'right' | 'left'; caretOffset: number }
type Viewport = { left: number; top: number; width: number; height: number }

const PADDING = 16
const GAP = 16
const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(value, Math.max(min, max)))

function computePosition(target: DOMRect, popup: { width: number; height: number }, viewport: Viewport): Position {
  const minX = viewport.left + PADDING
  const minY = viewport.top + PADDING
  const maxX = viewport.left + viewport.width - PADDING
  const maxY = viewport.top + viewport.height - PADDING
  const centerX = clamp(target.left + target.width / 2, minX, maxX)
  const centerY = clamp(target.top + target.height / 2, minY, maxY)
  const left = clamp(centerX - popup.width / 2, minX, maxX - popup.width)
  const top = clamp(centerY - popup.height / 2, minY, maxY - popup.height)
  const sides = {
    right: { top, left: target.right + GAP, caretSide: 'left' as const, room: maxX - target.right - GAP, needed: popup.width },
    left: { top, left: target.left - GAP - popup.width, caretSide: 'right' as const, room: target.left - GAP - minX, needed: popup.width },
    above: { top: target.top - GAP - popup.height, left, caretSide: 'bottom' as const, room: target.top - GAP - minY, needed: popup.height },
    below: { top: target.bottom + GAP, left, caretSide: 'top' as const, room: maxY - target.bottom - GAP, needed: popup.height },
  }
  // Open toward the middle of the screen; flip vertically on narrow screens.
  const horizontal = centerX < viewport.left + viewport.width / 2 ? [sides.right, sides.left] : [sides.left, sides.right]
  const vertical = sides.above.room >= sides.below.room ? [sides.above, sides.below] : [sides.below, sides.above]
  const candidates = [...horizontal, ...vertical]
  const selected = candidates.find((side) => side.room >= side.needed)
    ?? [...candidates].sort((a, b) => (b.room - b.needed) - (a.room - a.needed))[0]
  const position = {
    top: clamp(selected.top, minY, maxY - popup.height),
    left: clamp(selected.left, minX, maxX - popup.width),
    caretSide: selected.caretSide,
  }
  const horizontalCaret = selected.caretSide === 'top' || selected.caretSide === 'bottom'
  return {
    ...position,
    caretOffset: horizontalCaret
      ? clamp(centerX - position.left, 20, popup.width - 20)
      : clamp(centerY - position.top, 20, popup.height - 20),
  }
}

/** A non-modal introduction that follows its animated or draggable target. */
export function AnchoredCoachmark({
  targetSelector, title, body, variant = 'guide', step, dismissLabel = 'Got it', onDismiss,
}: {
  targetSelector: string
  title: string
  body: string
  variant?: 'guide' | 'tutor'
  step?: { current: number; total: number }
  dismissLabel?: string
  onDismiss: () => void
}) {
  const popupRef = useRef<HTMLDivElement>(null)
  const titleId = useId()
  const bodyId = useId()
  const Icon = variant === 'tutor' ? MessageCircle : BookOpen

  useLayoutEffect(() => {
    const popup = popupRef.current
    if (!popup) return
    let frame = 0
    let lastPosition = ''
    let observedTarget: Element | null = null
    // Transform changes happen after animation callbacks. Observe them as well
    // so the pointer stays attached in the same paint, rather than one frame late.
    const observer = new MutationObserver(() => reposition())

    const reposition = () => {
      const target = document.querySelector(targetSelector)
      if (target !== observedTarget) {
        observer.disconnect()
        observedTarget = target
        const options = { attributes: true, attributeFilter: ['style', 'class', 'hidden', 'inert', 'aria-hidden'] }
        if (target) observer.observe(target, options)
        if (target?.parentElement) observer.observe(target.parentElement, options)
      }
      const rect = target?.getBoundingClientRect()
      const visual = window.visualViewport
      const viewport = {
        left: visual?.offsetLeft ?? 0,
        top: visual?.offsetTop ?? 0,
        width: visual?.width ?? window.innerWidth,
        height: visual?.height ?? window.innerHeight,
      }
      const visible = target && rect && rect.width > 0 && rect.height > 0
        && rect.bottom > viewport.top && rect.top < viewport.top + viewport.height
        && rect.right > viewport.left && rect.left < viewport.left + viewport.width
        && !target.closest('[hidden], [inert], [aria-hidden="true"]')
        && getComputedStyle(target).visibility !== 'hidden'

      if (!visible) {
        popup.style.visibility = 'hidden'
        popup.setAttribute('aria-hidden', 'true')
        lastPosition = ''
      } else {
        const maxWidth = `${Math.max(0, viewport.width - PADDING * 2)}px`
        if (popup.style.maxWidth !== maxWidth) popup.style.maxWidth = maxWidth
        const pos = computePosition(rect, { width: popup.offsetWidth, height: popup.offsetHeight }, viewport)
        const nextPosition = `${pos.left},${pos.top},${pos.caretSide},${pos.caretOffset}`
        if (nextPosition !== lastPosition) {
          popup.style.left = `${pos.left}px`
          popup.style.top = `${pos.top}px`
          popup.style.setProperty('--caret-offset', `${pos.caretOffset}px`)
          popup.dataset.caret = pos.caretSide
          lastPosition = nextPosition
        }
        popup.style.visibility = 'visible'
        popup.removeAttribute('aria-hidden')
      }
    }
    const track = () => {
      reposition()
      frame = requestAnimationFrame(track)
    }
    track()
    return () => { cancelAnimationFrame(frame); observer.disconnect() }
  }, [targetSelector])

  return createPortal(
    <div ref={popupRef} className="anchored-coachmark" data-variant={variant}
      style={{ position: 'fixed', top: 0, left: 0, visibility: 'hidden' }}
      role="status" aria-live="polite" aria-labelledby={titleId} aria-describedby={bodyId} aria-hidden="true"
      onKeyDown={(event) => {
        if (event.key === 'Escape') { event.stopPropagation(); onDismiss() }
      }}>
      <header className="anchored-coachmark__header">
        <span className="anchored-coachmark__icon" aria-hidden="true"><Icon size={19} /></span>
        <div>
          <p className="anchored-coachmark__label">{variant === 'tutor' ? 'AI companion' : 'Around the map'}</p>
          <h2 id={titleId} className="anchored-coachmark__title">{title}</h2>
        </div>
        <button type="button" className="anchored-coachmark__close" aria-label={`Dismiss ${title} introduction`} onClick={onDismiss}>
          <X size={16} aria-hidden="true" />
        </button>
      </header>
      <p id={bodyId} className="anchored-coachmark__body">{body}</p>
      <footer className="anchored-coachmark__footer">
        {step ? <span className="anchored-coachmark__progress" aria-label={`Introduction ${step.current} of ${step.total}`}>
          {Array.from({ length: step.total }, (_, index) => <span key={index} data-active={index + 1 === step.current} />)}
          <span>{step.current} of {step.total}</span>
        </span> : <span />}
        <button type="button" className="anchored-coachmark__dismiss" onClick={onDismiss}>
          {dismissLabel}<ArrowRight size={14} aria-hidden="true" />
        </button>
      </footer>
    </div>, document.body,
  )
}
