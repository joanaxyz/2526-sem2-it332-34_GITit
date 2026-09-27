import { ArrowLeft, ArrowRight, Check, GripHorizontal, MoveDiagonal2, RotateCcw, X } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import type { CSSProperties, KeyboardEvent as ReactKeyboardEvent, PointerEvent as ReactPointerEvent, ReactNode } from 'react'
import { createPortal } from 'react-dom'

import { Button } from '@/shared/components/Button'
import {
  DEFAULT_CARD_HEIGHT,
  DESKTOP_CARD_WIDTH,
  HEADER_CLEARANCE,
  connectorPathFor,
  layoutFor,
  prefersReducedMotion,
  spotlightRect,
  VIEWPORT_GAP,
  type RectSnapshot,
  type TourLayout,
  type WorkspaceTourPlacement,
} from './gameplayWorkspaceTourLayout'

export type WorkspaceTourStep = {
  id: string
  selector: string
  icon: LucideIcon
  title: string
  body: ReactNode
  placement?: WorkspaceTourPlacement
  optional?: boolean
}

export type WorkspaceTourCloseReason = 'finish' | 'skip'

type CollapseVector = {
  x: number
  y: number
  scale: number
}

/** A card inside the guide: the main card, and (wide screens) the one beside it. */
type Pane = 'main' | 'aside'

type Size = { width: number; height: number }

type Position = { left: number; top: number }

type PaneBounds = { size: Size; minimum: Size; maximum: Size }

type TransformMode = 'move' | 'resize'

type TransformSession = {
  mode: 'move'
  pane: Pane
  pointerId: number
  startX: number
  startY: number
  frame: RectSnapshot
} | {
  mode: 'resize'
  pane: Pane
  pointerId: number
  startX: number
  startY: number
  bounds: PaneBounds
}

/** Layout, plus the main card's measured size when the cards float separately. */
type MeasuredLayout = TourLayout & { mainSize?: Size }

type ResolvedWorkspaceTourStep = {
  step: WorkspaceTourStep
  target: HTMLElement
}

const TARGET_GAP = 18
const ASIDE_GAP = 12
const TRANSFORM_BREAKPOINT = 600
const PANE_MINIMUMS: Record<Pane, Size> = {
  main: { width: 304, height: 220 },
  aside: { width: 240, height: 160 },
}
const KEYBOARD_TRANSFORM_STEP = 16

function frameAt(position: Position, size: Size): RectSnapshot {
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

function clampSize(size: Size, { minimum, maximum }: PaneBounds): Size {
  const clamp = (value: number, low: number, high: number) => Math.min(Math.max(value, Math.min(low, high)), high)
  return {
    width: clamp(size.width, minimum.width, maximum.width),
    height: clamp(size.height, minimum.height, maximum.height),
  }
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

function isVisible(element: HTMLElement) {
  const rect = element.getBoundingClientRect()
  const style = window.getComputedStyle(element)
  return !(
    rect.width <= 0 ||
    rect.height <= 0 ||
    style.display === 'none' ||
    style.visibility === 'hidden'
  )
}

function targetFor(step: WorkspaceTourStep) {
  const element = document.querySelector<HTMLElement>(step.selector)
  return element && isVisible(element) ? element : null
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

export function GameplayWorkspaceTour({
  label,
  finishLabel = 'Start playing',
  skipLabel = 'Skip tour',
  showSkip = true,
  skipIconOnly = false,
  showProgress = true,
  showActions = true,
  focusCard = true,
  finishDisabled = false,
  cardClassName,
  reveal,
  aside,
  asideWidth = 336,
  paneLabels = { main: 'main card', aside: 'side card' },
  steps,
  refreshKey,
  collapseTarget,
  transformable = false,
  onClose,
}: {
  label: string
  finishLabel?: string
  skipLabel?: string
  showSkip?: boolean
  /** Render the skip control as a bare close icon; `skipLabel` becomes its accessible name. */
  skipIconOnly?: boolean
  showProgress?: boolean
  /** Hide the footer for cards that update themselves instead of being stepped through. */
  showActions?: boolean
  /** Move focus into the card when it opens. Off for cards that sit beside an active input. */
  focusCard?: boolean
  finishDisabled?: boolean
  cardClassName?: string
  /** Selectors of regions to keep undimmed (the scenario, project files...). */
  reveal?: readonly string[]
  /**
   * A second card shown beside the main one, for wide screens. The guide then
   * becomes a frame holding both cards under one header, and each card sizes
   * on its own.
   */
  aside?: ReactNode
  asideWidth?: number
  /** Names of the two cards for their resize controls, e.g. "command card". */
  paneLabels?: Record<Pane, string>
  steps: readonly WorkspaceTourStep[]
  refreshKey?: string | number
  /** Animate the guide card into this control before closing. */
  collapseTarget?: string
  /** Let the learner move the guide and resize each card while keeping them in the viewport. */
  transformable?: boolean
  onClose: (reason: WorkspaceTourCloseReason) => void
}) {
  const markerId = `workspace-tour-arrow-${useId().replace(/:/g, '')}`
  const [cardElement, setCardElement] = useState<HTMLElement | null>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const [availableSteps, setAvailableSteps] = useState<readonly ResolvedWorkspaceTourStep[]>([])
  const [activeIndex, setActiveIndex] = useState(0)
  const [layout, setLayout] = useState<MeasuredLayout | null>(null)
  const [collapseVector, setCollapseVector] = useState<CollapseVector | null>(null)
  const [panePositions, setPanePositions] = useState<Partial<Record<Pane, Position>>>({})
  const [paneSizes, setPaneSizes] = useState<Partial<Record<Pane, Size>>>({})
  const [frontPane, setFrontPane] = useState<Pane>('main')
  const [transformMode, setTransformMode] = useState<TransformMode | null>(null)
  const transformSessionRef = useRef<TransformSession | null>(null)
  const closeTimerRef = useRef<number | null>(null)
  const activeResolvedStep = availableSteps[activeIndex]
  const activeStep = activeResolvedStep?.step
  const activeTarget = activeResolvedStep?.target
  const layoutReady = layout !== null
  // With a second card, each card floats on its own: the learner can pull
  // them apart, move either one, and size either one.
  const separate = Boolean(aside)
  const transformed = Object.values(panePositions).some(Boolean) || Object.values(paneSizes).some(Boolean)

  const resetTransform = useCallback(() => {
    setPanePositions({})
    setPaneSizes({})
  }, [])

  const resetPane = useCallback((pane: Pane) => {
    setPanePositions((positions) => ({ ...positions, [pane]: undefined }))
    setPaneSizes((sizes) => ({ ...sizes, [pane]: undefined }))
  }, [])

  const paneElement = useCallback((pane: Pane) => (
    separate
      ? cardElement?.querySelector<HTMLElement>(`[data-tour-pane="${pane}"]`) ?? null
      : cardElement
  ), [cardElement, separate])

  /** Where a card sits: pinned once moved or resized, else wherever layout put it. */
  const paneFrame = useCallback((pane: Pane): RectSnapshot | null => {
    const rect = paneElement(pane)?.getBoundingClientRect()
    if (!rect) return null
    return frameAt(panePositions[pane] ?? rect, paneSizes[pane] ?? rect)
  }, [paneElement, panePositions, paneSizes])

  /**
   * The first move or resize pins every card where it is, so from then on
   * each card only changes when the learner changes it.
   */
  const pinPanes = useCallback(() => {
    const pinned: Partial<Record<Pane, Position>> = {}
    for (const pane of separate ? ['main', 'aside'] as const : ['main'] as const) {
      const frame = paneFrame(pane)
      if (frame) pinned[pane] = { left: frame.left, top: frame.top }
    }
    setPanePositions((positions) => ({ ...pinned, ...positions }))
  }, [paneFrame, separate])

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

  const beginMove = useCallback((pane: Pane, event: ReactPointerEvent<HTMLButtonElement>) => {
    if (!transformable || window.innerWidth <= TRANSFORM_BREAKPOINT) return
    const frame = paneFrame(pane)
    if (!frame) return
    event.preventDefault()
    event.currentTarget.setPointerCapture?.(event.pointerId)
    transformSessionRef.current = {
      mode: 'move',
      pane,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      frame,
    }
    pinPanes()
    setPanePositions((positions) => ({ ...positions, [pane]: clampPosition(frame, frame) }))
    setFrontPane(pane)
    setTransformMode('move')
  }, [paneFrame, pinPanes, transformable])

  const beginResize = useCallback((pane: Pane, event: ReactPointerEvent<HTMLButtonElement>) => {
    if (!transformable || window.innerWidth <= TRANSFORM_BREAKPOINT) return
    const bounds = paneBounds(pane)
    if (!bounds) return
    event.preventDefault()
    event.currentTarget.setPointerCapture?.(event.pointerId)
    transformSessionRef.current = {
      mode: 'resize',
      pane,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      bounds,
    }
    pinPanes()
    setFrontPane(pane)
    setTransformMode('resize')
  }, [paneBounds, pinPanes, transformable])

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
    setPanePositions((positions) => ({
      ...positions,
      [pane]: clampPosition({ left: frame.left + delta.dx, top: frame.top + delta.dy }, frame),
    }))
    setFrontPane(pane)
  }, [paneFrame, pinPanes, resetPane])

  const resizeWithKeyboard = useCallback((pane: Pane, event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Home') {
      event.preventDefault()
      event.stopPropagation()
      setPaneSizes((sizes) => ({ ...sizes, [pane]: undefined }))
      return
    }
    const delta = arrowDelta(event)
    const bounds = paneBounds(pane)
    if (!delta || !bounds) return
    event.preventDefault()
    event.stopPropagation()
    pinPanes()
    setPaneSizes((sizes) => ({
      ...sizes,
      [pane]: clampSize({ width: bounds.size.width + delta.dx, height: bounds.size.height + delta.dy }, bounds),
    }))
    setFrontPane(pane)
  }, [paneBounds, pinPanes])

  const close = useCallback((reason: WorkspaceTourCloseReason) => {
    if (collapseVector) return
    const destination = collapseTarget
      ? document.querySelector<HTMLElement>(collapseTarget)
      : null
    if (!destination || !cardElement || prefersReducedMotion()) {
      onClose(reason)
      return
    }

    const cardRect = cardElement.getBoundingClientRect()
    const destinationRect = destination.getBoundingClientRect()
    if (!cardRect.width || !cardRect.height || !destinationRect.width || !destinationRect.height) {
      onClose(reason)
      return
    }

    setCollapseVector({
      x: destinationRect.left + destinationRect.width / 2 - (cardRect.left + cardRect.width / 2),
      y: destinationRect.top + destinationRect.height / 2 - (cardRect.top + cardRect.height / 2),
      scale: Math.max(0.08, Math.min(destinationRect.width / cardRect.width, destinationRect.height / cardRect.height)),
    })
    destination.classList.add('is-tour-destination')
    closeTimerRef.current = window.setTimeout(() => {
      destination.classList.remove('is-tour-destination')
      onClose(reason)
    }, 340)
  }, [cardElement, collapseTarget, collapseVector, onClose])

  useEffect(() => () => {
    if (closeTimerRef.current !== null) window.clearTimeout(closeTimerRef.current)
    if (collapseTarget) {
      document.querySelector<HTMLElement>(collapseTarget)?.classList.remove('is-tour-destination')
    }
  }, [collapseTarget])

  useEffect(() => {
    if (!transformable) return

    const handlePointerMove = (event: PointerEvent) => {
      const session = transformSessionRef.current
      if (!session || event.pointerId !== session.pointerId) return
      const dx = event.clientX - session.startX
      const dy = event.clientY - session.startY
      if (session.mode === 'move') {
        const { pane, frame } = session
        setPanePositions((positions) => ({
          ...positions,
          [pane]: clampPosition({ left: frame.left + dx, top: frame.top + dy }, frame),
        }))
        return
      }
      const { pane, bounds } = session
      setPaneSizes((sizes) => ({
        ...sizes,
        [pane]: clampSize({ width: bounds.size.width + dx, height: bounds.size.height + dy }, bounds),
      }))
    }
    const finishTransform = (event: PointerEvent) => {
      if (event.pointerId !== transformSessionRef.current?.pointerId) return
      transformSessionRef.current = null
      setTransformMode(null)
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
  }, [transformable])

  useEffect(() => {
    if (!transformable) return
    // A smaller window shrinks resized cards to fit and keeps every card in view.
    const keepCardsVisible = () => {
      if (window.innerWidth <= TRANSFORM_BREAKPOINT) {
        resetTransform()
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
      setPaneSizes((sizes) => {
        const next = { ...sizes }
        for (const pane of ['main', 'aside'] as const) {
          const size = next[pane]
          if (size) next[pane] = fit(size)
        }
        return next
      })
      setPanePositions((positions) => {
        const next = { ...positions }
        for (const pane of ['main', 'aside'] as const) {
          const position = next[pane]
          const frame = frames[pane]
          if (position && frame) next[pane] = clampPosition(position, fit(frame))
        }
        return next
      })
    }
    window.addEventListener('resize', keepCardsVisible)
    return () => window.removeEventListener('resize', keepCardsVisible)
  }, [paneFrame, resetTransform, separate, transformable])

  useEffect(() => {
    resetTransform()
    transformSessionRef.current = null
    setTransformMode(null)
  }, [activeStep?.id, refreshKey, resetTransform])

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
      // Separate cards: the section spans the viewport, so measure the cards themselves.
      const panes = aside
        ? [...(cardElement?.querySelectorAll<HTMLElement>('[data-tour-pane]') ?? [])]
        : []
      const mainPane = panes.find((pane) => pane.dataset.tourPane === 'main')?.getBoundingClientRect()
      const cardHeight = (aside
        ? Math.max(0, ...panes.map((pane) => pane.getBoundingClientRect().height))
        : cardElement?.getBoundingClientRect().height) || DEFAULT_CARD_HEIGHT
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

      // Separate cards are placed side by side, as one box, until the learner moves them.
      const width = aside ? DESKTOP_CARD_WIDTH + ASIDE_GAP + asideWidth : DESKTOP_CARD_WIDTH
      const reveals = (reveal ?? [])
        .map((selector) => document.querySelector<HTMLElement>(selector))
        .flatMap((element) => (element && isVisible(element) ? [element.getBoundingClientRect()] : []))
        .map((box) => ({
          top: box.top, right: box.right, bottom: box.bottom, left: box.left, width: box.width, height: box.height,
        }))
      setLayout({
        ...layoutFor(rect, activeStep.placement ?? 'bottom', cardHeight, width),
        reveals,
        ...(mainPane ? { mainSize: { width: mainPane.width, height: mainPane.height } } : {}),
      })
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
    if (cardElement) {
      observer.observe(cardElement)
      cardElement.querySelectorAll('[data-tour-pane]').forEach((pane) => observer.observe(pane))
    }
    for (const selector of reveal ?? []) {
      const element = document.querySelector(selector)
      if (element) observer.observe(element)
    }
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
  }, [activeStep, activeTarget, aside, asideWidth, cardElement, reveal])

  useEffect(() => {
    if (!focusCard || !activeStep || !layoutReady) return
    const frameId = window.requestAnimationFrame(() => cardElement?.focus())
    return () => window.cancelAnimationFrame(frameId)
  }, [activeStep, cardElement, focusCard, layoutReady])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (availableSteps.length === 0) return
      if (event.key === 'Escape' && showSkip) {
        event.preventDefault()
        close('skip')
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
  }, [activeIndex, availableSteps.length, close, showSkip])

  if (!activeStep || !layout || typeof document === 'undefined') return null

  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  // Until the learner moves one, the cards sit side by side where layout put them.
  const mainWidth = paneSizes.main?.width ?? (separate ? DESKTOP_CARD_WIDTH : layout.card.width)
  const autoPositions: Record<Pane, Position> = {
    main: layout.card,
    aside: { left: layout.card.left + mainWidth + ASIDE_GAP, top: layout.card.top },
  }
  const positionOf = (pane: Pane) => panePositions[pane] ?? autoPositions[pane]
  const mainFrame = frameAt(positionOf('main'), paneSizes.main ?? layout.mainSize ?? layout.card)
  // The connector leaves the card that explains the target: the main one.
  const arrowPath = transformed
    ? connectorPathFor(mainFrame, layout.target)
    : layout.arrowPath
  const targetVisible = layout.target.bottom > HEADER_CLEARANCE
    && layout.target.top < viewportHeight - VIEWPORT_GAP
    && layout.target.right > 0 && layout.target.left < viewportWidth
  const spotlight = spotlightRect(layout.target, viewportWidth, viewportHeight)
  const holes = [
    ...(targetVisible ? [spotlight] : []),
    ...(layout.reveals ?? []).map((box) => spotlightRect(box, viewportWidth, viewportHeight, 3)),
  ]
  // Resolved steps keep the objects they were matched with; render the latest
  // content for the same step so a step can update in place (tabs, feedback).
  const shownStep = steps.find((step) => step.id === activeStep.id) ?? activeStep
  const Icon = shownStep.icon
  const finalStep = activeIndex === availableSteps.length - 1
  // A long final CTA has priority over the optional keyboard hint. Keeping all
  // three footer items in this fixed-width card can push the action offscreen.
  const compactActions = !showProgress || (finalStep && finishLabel.length > 16)
  const titleId = `${markerId}-title`
  const bodyId = `${markerId}-body`
  const cardStyle = {
    ...(separate ? {} : {
      left: mainFrame.left,
      top: mainFrame.top,
      width: mainFrame.width,
      ...(paneSizes.main ? { height: paneSizes.main.height, maxHeight: paneSizes.main.height } : {}),
    }),
    ...(!transformed && layout.room ? { '--workspace-tour-room': `${layout.room}px` } : {}),
    ...(collapseVector ? {
      '--workspace-tour-collapse-x': `${collapseVector.x}px`,
      '--workspace-tour-collapse-y': `${collapseVector.y}px`,
      '--workspace-tour-collapse-scale': collapseVector.scale,
    } : {}),
  } as CSSProperties
  const paneStyle = (pane: Pane, defaultWidth: number): CSSProperties => {
    const size = paneSizes[pane]
    const position = positionOf(pane)
    return {
      left: position.left,
      top: position.top,
      ...(size ? { width: size.width, height: size.height, maxHeight: 'none' } : { width: defaultWidth }),
    }
  }
  const cardName = (pane: Pane) => (separate ? paneLabels[pane] : label.toLowerCase())
  const moveHandle = (pane: Pane, className = '') => transformable ? (
    <button
      type="button"
      className={`workspace-tour__transform-control is-move${className}`}
      aria-label={`Move ${cardName(pane)}`}
      title="Drag to move. Arrow keys move; Shift moves farther; Home resets."
      onPointerDown={(event) => beginMove(pane, event)}
      onKeyDown={(event) => moveWithKeyboard(pane, event)}
    >
      <GripHorizontal aria-hidden="true" />
    </button>
  ) : null
  const resizeHandle = (pane: Pane) => transformable ? (
    <button
      type="button"
      className="workspace-tour__resize-handle"
      aria-label={`Resize ${cardName(pane)}`}
      title="Drag to resize. Arrow keys resize; Shift resizes farther; Home resets."
      onPointerDown={(event) => beginResize(pane, event)}
      onKeyDown={(event) => resizeWithKeyboard(pane, event)}
    >
      <MoveDiagonal2 aria-hidden="true" />
    </button>
  ) : null

  const content = (
    <>
      <header className="workspace-tour__header">
        <div className="workspace-tour__meta">
          <span className="workspace-tour__eyebrow">{label}</span>
          {availableSteps.length > 1 ? (
            <span className="workspace-tour__count">
              {activeIndex + 1} / {availableSteps.length}
            </span>
          ) : null}
        </div>
        {transformable || showSkip ? <div className="workspace-tour__header-actions">
          {moveHandle('main')}
          {transformable && transformed ? <button
            type="button"
            className="workspace-tour__transform-control"
            aria-label={`Reset ${label.toLowerCase()} size and position`}
            title="Reset size and position"
            onClick={resetTransform}
          >
            <RotateCcw aria-hidden="true" />
          </button> : null}
          {showSkip ? <button
            type="button"
            className={`workspace-tour__skip${skipIconOnly ? ' is-icon-only' : ''}`}
            aria-label={skipIconOnly ? skipLabel : undefined}
            title={skipIconOnly ? skipLabel : undefined}
            onClick={() => close('skip')}
          >
            {skipIconOnly ? null : skipLabel}
            <X aria-hidden="true" />
          </button> : null}
        </div> : null}
      </header>

      <div className="workspace-tour__message" aria-live="polite">
        <span className="workspace-tour__icon" aria-hidden="true">
          <Icon />
        </span>
        <div>
          <h2 id={titleId}>{shownStep.title}</h2>
          <div id={bodyId} className="workspace-tour__body">{shownStep.body}</div>
        </div>
      </div>

      {showProgress ? <nav className="workspace-tour__progress" aria-label={`${label} steps`}>
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
      </nav> : null}

      {showActions ? <footer className={`workspace-tour__actions${compactActions ? ' is-compact' : ''}`}>
        {showProgress ? <Button
          type="button"
          variant="ghost"
          size="sm"
          className="workspace-tour__back"
          disabled={activeIndex === 0}
          onClick={() => setActiveIndex((index) => Math.max(0, index - 1))}
        >
          <ArrowLeft aria-hidden="true" />
          Back
        </Button> : null}
        {showProgress ? <span className="workspace-tour__shortcut">Alt + arrows</span> : null}
        <Button
          type="button"
          size="sm"
          className="workspace-tour__next"
          disabled={finishDisabled}
          onClick={() => {
            if (finalStep) close('finish')
            else setActiveIndex((index) => index + 1)
          }}
        >
          {finalStep ? <Check aria-hidden="true" /> : null}
          {finalStep ? finishLabel : 'Next'}
          {finalStep ? null : <ArrowRight aria-hidden="true" />}
        </Button>
      </footer> : null}
    </>
  )

  return createPortal(
    <div
      className="workspace-tour"
      data-closing={collapseVector ? 'true' : undefined}
      data-transforming={transformMode ?? undefined}
      data-testid="workspace-tour"
    >
      {/* One dimming layer with cut-outs: the spotlit target plus any revealed
          regions stay readable, since tours explain them rather than hide them. */}
      <svg
        className="workspace-tour__veil"
        width={viewportWidth}
        height={viewportHeight}
        aria-hidden="true"
      >
        <defs>
          <mask id={`${markerId}-veil`} maskUnits="userSpaceOnUse" x="0" y="0" width={viewportWidth} height={viewportHeight}>
            <rect width={viewportWidth} height={viewportHeight} fill="white" />
            {holes.map((hole, index) => (
              <rect
                key={index}
                x={hole.left}
                y={hole.top}
                width={hole.width}
                height={hole.height}
                rx="10"
                fill="black"
              />
            ))}
          </mask>
        </defs>
        <rect width={viewportWidth} height={viewportHeight} mask={`url(#${markerId}-veil)`} />
      </svg>

      {targetVisible ? <><div
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
        <path className="workspace-tour__connector-glow" d={arrowPath} />
        <path
          className="workspace-tour__connector-line"
          d={arrowPath}
          markerEnd={`url(#${markerId})`}
        />
      </svg></> : null}

      <section
        ref={setCardElement}
        className={`workspace-tour__card${separate ? ' has-aside' : ''}${transformable ? ' is-transformable' : ''}${transformed ? ' is-transformed' : ''}${collapseVector ? ' is-collapsing' : ''}${cardClassName ? ` ${cardClassName}` : ''}`}
        key={activeStep.id}
        style={cardStyle}
        role="dialog"
        aria-modal="false"
        aria-label={label}
        aria-labelledby={titleId}
        aria-describedby={bodyId}
        tabIndex={-1}
      >
        {separate ? (
          // No frame around the cards: each one floats, moves, and sizes on its own.
          <>
            <div
              className={`workspace-tour__pane workspace-tour__main${frontPane === 'main' ? ' is-front' : ''}`}
              data-tour-pane="main"
              style={paneStyle('main', DESKTOP_CARD_WIDTH)}
              onPointerDown={() => setFrontPane('main')}
            >
              {content}
              {resizeHandle('main')}
            </div>
            <aside
              className={`workspace-tour__pane workspace-tour__aside${frontPane === 'aside' ? ' is-front' : ''}`}
              data-tour-pane="aside"
              style={paneStyle('aside', asideWidth)}
              onPointerDown={() => setFrontPane('aside')}
            >
              {moveHandle('aside', ' workspace-tour__pane-move')}
              <div className="workspace-tour__pane-scroll">{aside}</div>
              {resizeHandle('aside')}
            </aside>
          </>
        ) : (
          <>
            {content}
            {resizeHandle('main')}
          </>
        )}
      </section>
    </div>,
    document.body,
  )
}
