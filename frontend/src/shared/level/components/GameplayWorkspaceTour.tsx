import { ArrowLeft, ArrowRight, Check, X } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { createPortal } from 'react-dom'

import { Button } from '@/shared/components/Button'

export type WorkspaceTourPlacement = 'top' | 'right' | 'bottom' | 'left'

export type WorkspaceTourStep = {
  id: string
  selector: string
  icon: LucideIcon
  title: string
  body: string
  placement?: WorkspaceTourPlacement
  optional?: boolean
}

export type WorkspaceTourCloseReason = 'finish' | 'skip'

type RectSnapshot = {
  top: number
  right: number
  bottom: number
  left: number
  width: number
  height: number
}

type Point = { x: number; y: number }

type TourLayout = {
  target: RectSnapshot
  card: RectSnapshot
  arrowPath: string
}

type ResolvedWorkspaceTourStep = {
  step: WorkspaceTourStep
  target: HTMLElement
}

const VIEWPORT_GAP = 16
const TARGET_GAP = 18
const TARGET_PADDING = 9
const HEADER_CLEARANCE = 76
const DEFAULT_CARD_HEIGHT = 236
const DESKTOP_CARD_WIDTH = 352

function rectSnapshot(rect: DOMRect): RectSnapshot {
  return {
    top: rect.top,
    right: rect.right,
    bottom: rect.bottom,
    left: rect.left,
    width: rect.width,
    height: rect.height,
  }
}

function targetFor(step: WorkspaceTourStep) {
  const element = document.querySelector<HTMLElement>(step.selector)
  if (!element) return null
  const rect = element.getBoundingClientRect()
  const style = window.getComputedStyle(element)
  if (
    rect.width <= 0 ||
    rect.height <= 0 ||
    style.display === 'none' ||
    style.visibility === 'hidden'
  ) {
    return null
  }
  return element
}

function sameResolvedSteps(
  left: readonly ResolvedWorkspaceTourStep[],
  right: readonly ResolvedWorkspaceTourStep[],
) {
  return (
    left.length === right.length &&
    left.every(
      (resolved, index) =>
        resolved.step.id === right[index]?.step.id && resolved.target === right[index]?.target,
    )
  )
}

function candidateFor(
  placement: WorkspaceTourPlacement,
  target: RectSnapshot,
  width: number,
  height: number,
) {
  const centerX = target.left + target.width / 2
  const centerY = target.top + target.height / 2
  switch (placement) {
    case 'top':
      return { left: centerX - width / 2, top: target.top - height - TARGET_GAP }
    case 'right':
      return { left: target.right + TARGET_GAP, top: centerY - height / 2 }
    case 'left':
      return { left: target.left - width - TARGET_GAP, top: centerY - height / 2 }
    default:
      return { left: centerX - width / 2, top: target.bottom + TARGET_GAP }
  }
}

function cardFits(
  card: RectSnapshot,
  target: RectSnapshot,
  viewportWidth: number,
  viewportHeight: number,
) {
  const inViewport =
    card.left >= VIEWPORT_GAP &&
    card.right <= viewportWidth - VIEWPORT_GAP &&
    card.top >= VIEWPORT_GAP &&
    card.bottom <= viewportHeight - VIEWPORT_GAP
  const clearsTarget =
    card.right <= target.left - TARGET_GAP ||
    card.left >= target.right + TARGET_GAP ||
    card.bottom <= target.top - TARGET_GAP ||
    card.top >= target.bottom + TARGET_GAP
  return inViewport && clearsTarget
}

function cardRect(left: number, top: number, width: number, height: number): RectSnapshot {
  return { left, top, right: left + width, bottom: top + height, width, height }
}

function connectorPoints(card: RectSnapshot, target: RectSnapshot): { start: Point; end: Point } {
  const cardCenter = { x: card.left + card.width / 2, y: card.top + card.height / 2 }
  const targetCenter = { x: target.left + target.width / 2, y: target.top + target.height / 2 }

  if (card.bottom <= target.top) {
    return {
      start: { x: cardCenter.x, y: card.bottom },
      end: { x: targetCenter.x, y: target.top },
    }
  }
  if (card.top >= target.bottom) {
    return {
      start: { x: cardCenter.x, y: card.top },
      end: { x: targetCenter.x, y: target.bottom },
    }
  }
  if (card.right <= target.left) {
    return {
      start: { x: card.right, y: cardCenter.y },
      end: { x: target.left, y: targetCenter.y },
    }
  }
  return {
    start: { x: card.left, y: cardCenter.y },
    end: { x: target.right, y: targetCenter.y },
  }
}

function layoutFor(
  targetRect: DOMRect,
  preferredPlacement: WorkspaceTourPlacement,
  measuredCardHeight: number,
): TourLayout {
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const cardWidth = Math.min(DESKTOP_CARD_WIDTH, viewportWidth - VIEWPORT_GAP * 2)
  const cardHeight = Math.min(measuredCardHeight || DEFAULT_CARD_HEIGHT, viewportHeight - VIEWPORT_GAP * 2)
  const target = rectSnapshot(targetRect)
  const placements = [preferredPlacement, 'bottom', 'top', 'right', 'left'].filter(
    (placement, index, items) => items.indexOf(placement) === index,
  ) as WorkspaceTourPlacement[]

  let card = cardRect(VIEWPORT_GAP, HEADER_CLEARANCE, cardWidth, cardHeight)
  for (const placement of placements) {
    const candidate = candidateFor(placement, target, cardWidth, cardHeight)
    const nextCard = cardRect(candidate.left, candidate.top, cardWidth, cardHeight)
    if (cardFits(nextCard, target, viewportWidth, viewportHeight)) {
      card = nextCard
      break
    }
  }

  if (!cardFits(card, target, viewportWidth, viewportHeight)) {
    const placeAbove = target.top > viewportHeight - target.bottom
    const fallbackTop = placeAbove
      ? target.top - cardHeight - TARGET_GAP
      : target.bottom + TARGET_GAP
    const fallbackLeft = target.left + target.width / 2 - cardWidth / 2
    card = cardRect(
      Math.min(Math.max(fallbackLeft, VIEWPORT_GAP), viewportWidth - cardWidth - VIEWPORT_GAP),
      Math.min(Math.max(fallbackTop, VIEWPORT_GAP), viewportHeight - cardHeight - VIEWPORT_GAP),
      cardWidth,
      cardHeight,
    )
  }

  const { start, end } = connectorPoints(card, target)
  const control = {
    x: start.x + (end.x - start.x) * 0.54,
    y: start.y + (end.y - start.y) * 0.38,
  }

  return {
    target,
    card,
    arrowPath: `M ${start.x} ${start.y} Q ${control.x} ${control.y} ${end.x} ${end.y}`,
  }
}

function spotlightRect(target: RectSnapshot, viewportWidth: number, viewportHeight: number) {
  const left = Math.max(0, target.left - TARGET_PADDING)
  const top = Math.max(0, target.top - TARGET_PADDING)
  const right = Math.min(viewportWidth, target.right + TARGET_PADDING)
  const bottom = Math.min(viewportHeight, target.bottom + TARGET_PADDING)
  return { left, top, right, bottom, width: right - left, height: bottom - top }
}

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

export function GameplayWorkspaceTour({
  label,
  finishLabel = 'Start playing',
  steps,
  refreshKey,
  onClose,
}: {
  label: string
  finishLabel?: string
  steps: readonly WorkspaceTourStep[]
  refreshKey?: string | number
  onClose: (reason: WorkspaceTourCloseReason) => void
}) {
  const markerId = `workspace-tour-arrow-${useId().replace(/:/g, '')}`
  const [cardElement, setCardElement] = useState<HTMLElement | null>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const [availableSteps, setAvailableSteps] = useState<readonly ResolvedWorkspaceTourStep[]>([])
  const [activeIndex, setActiveIndex] = useState(0)
  const [layout, setLayout] = useState<TourLayout | null>(null)
  const activeResolvedStep = availableSteps[activeIndex]
  const activeStep = activeResolvedStep?.step
  const activeTarget = activeResolvedStep?.target
  const layoutReady = layout !== null

  useEffect(() => {
    previousFocusRef.current = document.activeElement as HTMLElement | null
    return () => {
      const previous = previousFocusRef.current
      if (previous?.isConnected) previous.focus()
    }
  }, [])

  useEffect(() => {
    let frameId = 0
    const resolveSteps = () => {
      window.cancelAnimationFrame(frameId)
      frameId = window.requestAnimationFrame(() => {
        const candidates = steps.map((step) => ({ step, target: targetFor(step) }))
        if (candidates.some(({ step, target }) => !step.optional && !target)) {
          setAvailableSteps((current) => (current.length === 0 ? current : []))
          return
        }
        const resolved = candidates.flatMap(({ step, target }) =>
          target ? [{ step, target }] : [],
        )
        setAvailableSteps((current) =>
          sameResolvedSteps(current, resolved) ? current : resolved,
        )
      })
    }

    resolveSteps()
    const observer = new MutationObserver(resolveSteps)
    observer.observe(document.body, { childList: true, subtree: true })
    window.addEventListener('resize', resolveSteps)
    return () => {
      window.cancelAnimationFrame(frameId)
      observer.disconnect()
      window.removeEventListener('resize', resolveSteps)
    }
  }, [refreshKey, steps])

  useEffect(() => {
    if (activeIndex < availableSteps.length) return
    setActiveIndex(Math.max(0, availableSteps.length - 1))
  }, [activeIndex, availableSteps.length])

  useLayoutEffect(() => {
    if (!activeStep || !activeTarget) {
      setLayout(null)
      return
    }

    const target = activeTarget

    let frameId = 0
    let settleTimer = 0
    let scrolled = false
    const previousScrollMarginTop = target.style.scrollMarginTop
    target.style.scrollMarginTop = `${HEADER_CLEARANCE + VIEWPORT_GAP}px`

    const measureNow = () => {
      const rect = target.getBoundingClientRect()
      const cardHeight = cardElement?.getBoundingClientRect().height || DEFAULT_CARD_HEIGHT
      const narrow = window.innerWidth <= 900
      const needsScroll =
        rect.top < HEADER_CLEARANCE ||
        rect.bottom > window.innerHeight - VIEWPORT_GAP ||
        (narrow && rect.bottom + cardHeight + TARGET_GAP > window.innerHeight - VIEWPORT_GAP)

      if (needsScroll && !scrolled) {
        scrolled = true
        target.scrollIntoView({
          behavior: prefersReducedMotion() ? 'auto' : 'smooth',
          block: 'start',
          inline: 'nearest',
        })
        settleTimer = window.setTimeout(measure, prefersReducedMotion() ? 0 : 240)
        return
      }

      setLayout(layoutFor(rect, activeStep.placement ?? 'bottom', cardHeight))
    }

    const measure = () => {
      if (frameId) return
      frameId = window.requestAnimationFrame(() => {
        frameId = 0
        measureNow()
      })
    }

    if (!cardElement) setLayout(null)
    measureNow()
    const observer = new ResizeObserver(measure)
    observer.observe(target)
    if (cardElement) observer.observe(cardElement)
    window.addEventListener('resize', measure)
    window.addEventListener('scroll', measure, true)
    return () => {
      target.style.scrollMarginTop = previousScrollMarginTop
      window.cancelAnimationFrame(frameId)
      window.clearTimeout(settleTimer)
      observer.disconnect()
      window.removeEventListener('resize', measure)
      window.removeEventListener('scroll', measure, true)
    }
  }, [activeStep, activeTarget, cardElement])

  useEffect(() => {
    if (!activeStep || !layoutReady) return
    const frameId = window.requestAnimationFrame(() => cardElement?.focus())
    return () => window.cancelAnimationFrame(frameId)
  }, [activeStep, cardElement, layoutReady])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (availableSteps.length === 0) return
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose('skip')
        return
      }
      if (!event.altKey) return
      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        setActiveIndex((index) => Math.max(0, index - 1))
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault()
        setActiveIndex((index) => Math.min(availableSteps.length - 1, index + 1))
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [activeIndex, availableSteps.length, onClose])

  if (!activeStep || !layout || typeof document === 'undefined') return null

  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const spotlight = spotlightRect(layout.target, viewportWidth, viewportHeight)
  const Icon = activeStep.icon
  const finalStep = activeIndex === availableSteps.length - 1
  // A long final CTA has priority over the optional keyboard hint. Keeping all
  // three footer items in this fixed-width card can push the action offscreen.
  const compactActions = finalStep && finishLabel.length > 16
  const titleId = `${markerId}-title`
  const bodyId = `${markerId}-body`
  const cardStyle = {
    left: layout.card.left,
    top: layout.card.top,
    width: layout.card.width,
  } as CSSProperties

  return createPortal(
    <div className="workspace-tour" data-testid="workspace-tour">
      <div className="workspace-tour__scrim" style={{ left: 0, top: 0, width: '100%', height: spotlight.top }} />
      <div
        className="workspace-tour__scrim"
        style={{ left: 0, top: spotlight.bottom, width: '100%', height: viewportHeight - spotlight.bottom }}
      />
      <div
        className="workspace-tour__scrim"
        style={{ left: 0, top: spotlight.top, width: spotlight.left, height: spotlight.height }}
      />
      <div
        className="workspace-tour__scrim"
        style={{
          left: spotlight.right,
          top: spotlight.top,
          width: viewportWidth - spotlight.right,
          height: spotlight.height,
        }}
      />

      <div
        className="workspace-tour__spotlight"
        data-testid="workspace-tour-spotlight"
        style={{
          left: spotlight.left,
          top: spotlight.top,
          width: spotlight.width,
          height: spotlight.height,
        }}
      >
        <span className="workspace-tour__beacon" aria-hidden="true" />
      </div>

      <svg className="workspace-tour__connector" aria-hidden="true">
        <defs>
          <marker
            id={markerId}
            markerHeight="10"
            markerWidth="10"
            orient="auto"
            refX="8"
            refY="4"
          >
            <path d="M0,0 L0,8 L9,4 z" />
          </marker>
        </defs>
        <path className="workspace-tour__connector-glow" d={layout.arrowPath} />
        <path
          className="workspace-tour__connector-line"
          d={layout.arrowPath}
          markerEnd={`url(#${markerId})`}
        />
      </svg>

      <section
        ref={setCardElement}
        className="workspace-tour__card"
        key={activeStep.id}
        style={cardStyle}
        role="dialog"
        aria-modal="false"
        aria-label={label}
        aria-labelledby={titleId}
        aria-describedby={bodyId}
        tabIndex={-1}
      >
        <header className="workspace-tour__header">
          <div className="workspace-tour__meta">
            <span className="workspace-tour__eyebrow">{label}</span>
            <span className="workspace-tour__count">
              {activeIndex + 1} / {availableSteps.length}
            </span>
          </div>
          <button
            type="button"
            className="workspace-tour__skip"
            onClick={() => onClose('skip')}
          >
            Skip tour
            <X aria-hidden="true" />
          </button>
        </header>

        <div className="workspace-tour__message" aria-live="polite">
          <span className="workspace-tour__icon" aria-hidden="true">
            <Icon />
          </span>
          <div>
            <h2 id={titleId}>{activeStep.title}</h2>
            <p id={bodyId}>{activeStep.body}</p>
          </div>
        </div>

        <nav className="workspace-tour__progress" aria-label={`${label} steps`}>
          {availableSteps.map(({ step }, index) => (
            <button
              type="button"
              key={step.id}
              className={index <= activeIndex ? 'is-complete' : undefined}
              aria-current={index === activeIndex ? 'step' : undefined}
              aria-label={`Go to step ${index + 1}: ${step.title}`}
              onClick={() => setActiveIndex(index)}
            >
              <span aria-hidden="true" />
            </button>
          ))}
        </nav>

        <footer className={`workspace-tour__actions${compactActions ? ' is-compact' : ''}`}>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="workspace-tour__back"
            disabled={activeIndex === 0}
            onClick={() => setActiveIndex((index) => Math.max(0, index - 1))}
          >
            <ArrowLeft aria-hidden="true" />
            Back
          </Button>
          <span className="workspace-tour__shortcut">Alt + arrows</span>
          <Button
            type="button"
            size="sm"
            className="workspace-tour__next"
            onClick={() => {
              if (finalStep) onClose('finish')
              else setActiveIndex((index) => index + 1)
            }}
          >
            {finalStep ? <Check aria-hidden="true" /> : null}
            {finalStep ? finishLabel : 'Next'}
            {finalStep ? null : <ArrowRight aria-hidden="true" />}
          </Button>
        </footer>
      </section>
    </div>,
    document.body,
  )
}
