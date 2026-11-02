import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'

import { GameplayWorkspaceTourOverlay } from './GameplayWorkspaceTourOverlay'
import {
  DEFAULT_CARD_HEIGHT,
  DESKTOP_CARD_WIDTH,
  HEADER_CLEARANCE,
  layoutFor,
  layoutForPanes,
  prefersReducedMotion,
  VIEWPORT_GAP,
  type WorkspaceTourPaneLayout,
} from './gameplayWorkspaceTourLayout'
import type {
  CollapseVector,
  MeasuredWorkspaceTourLayout,
  ResolvedWorkspaceTourStep,
  WorkspaceTourCloseReason,
  WorkspaceTourPane,
  WorkspaceTourStep,
} from './gameplayWorkspaceTourTypes'
import { useWorkspaceTourTransform } from './useWorkspaceTourTransform'

export type { WorkspaceTourCloseReason, WorkspaceTourStep } from './gameplayWorkspaceTourTypes'

const TARGET_GAP = 18
const ASIDE_GAP = 12

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
  showSpeaker = true,
  controlsWithSpeaker = false,
  showActions = true,
  focusCard = true,
  finishDisabled = false,
  cardClassName,
  cardWidth = DESKTOP_CARD_WIDTH,
  reveal,
  aside,
  asideWidth = 336,
  paneLayout,
  paneLabels = { main: 'main card', aside: 'side card' },
  steps,
  refreshKey,
  collapseTarget,
  closeOnOutsideClick,
  transformable = false,
  transformPreferenceKey,
  onClose,
}: {
  label: string
  finishLabel?: string
  skipLabel?: string
  showSkip?: boolean
  /** Render the skip control as a bare close icon; `skipLabel` becomes its accessible name. */
  skipIconOnly?: boolean
  showProgress?: boolean
  showSpeaker?: boolean
  /** Omit the header and place controls below the clickable speaker portrait. */
  controlsWithSpeaker?: boolean
  /** Hide the footer for cards that update themselves instead of being stepped through. */
  showActions?: boolean
  /** Move focus into the card when it opens. Off for cards that sit beside an active input. */
  focusCard?: boolean
  finishDisabled?: boolean
  cardClassName?: string
  /** Preferred outer width, including the speaker; shrinks to fit narrow viewports. */
  cardWidth?: number
  /** Selectors of regions to keep undimmed (the scenario, project files...). */
  reveal?: readonly string[]
  /** A second card shown beside the main one on wide screens. */
  aside?: ReactNode
  asideWidth?: number
  /** Initial sizes and top alignment for a pair of cards; manual transforms take priority. */
  paneLayout?: WorkspaceTourPaneLayout
  /** Names of the two cards for their resize controls, e.g. "command card". */
  paneLabels?: Record<WorkspaceTourPane, string>
  steps: readonly WorkspaceTourStep[]
  refreshKey?: string | number
  /** Animate the guide card into this control before closing. */
  collapseTarget?: string
  /**
   * Put the card away when the learner clicks outside it, as Escape does. Clicks
   * on its target and in the `except` regions (a companion window) are inside.
   */
  closeOnOutsideClick?: { except?: readonly string[] }
  /** Let the learner move and resize guide cards while keeping them in the viewport. */
  transformable?: boolean
  /** Persist transformable card positions and sizes in the browser under this preference key. */
  transformPreferenceKey?: string
  onClose: (reason: WorkspaceTourCloseReason) => void
}) {
  const markerId = `workspace-tour-arrow-${useId().replace(/:/g, '')}`
  const [cardElement, setCardElement] = useState<HTMLElement | null>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const [availableSteps, setAvailableSteps] = useState<readonly ResolvedWorkspaceTourStep[]>([])
  const [activeIndex, setActiveIndex] = useState(0)
  const [layout, setLayout] = useState<MeasuredWorkspaceTourLayout | null>(null)
  const [collapseVector, setCollapseVector] = useState<CollapseVector | null>(null)
  const closeTimerRef = useRef<number | null>(null)
  const activeResolvedStep = availableSteps[activeIndex]
  const activeStep = activeResolvedStep?.step
  const activeTarget = activeResolvedStep?.target
  const layoutReady = layout !== null
  const separate = Boolean(aside)
  const transform = useWorkspaceTourTransform({
    cardElement,
    separate,
    transformable,
    transformPreferenceKey,
    activeStepId: activeStep?.id,
    refreshKey,
  })

  const close = useCallback((reason: WorkspaceTourCloseReason) => {
    if (collapseVector) return
    // A click elsewhere moves the learner on: focus stays where they clicked.
    if (reason === 'outside') previousFocusRef.current = null
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
      const panes = aside
        ? [...(cardElement?.querySelectorAll<HTMLElement>('[data-tour-pane]') ?? [])]
        : []
      const mainPane = panes.find((pane) => pane.dataset.tourPane === 'main')?.getBoundingClientRect()
      const bubble = cardElement?.querySelector<HTMLElement>('.mascot-message__bubble')?.getBoundingClientRect()
      const mainRect = mainPane ?? cardElement?.getBoundingClientRect()
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

      const width = aside ? DESKTOP_CARD_WIDTH + ASIDE_GAP + asideWidth : cardWidth
      const bubbleInset = bubble && mainRect ? Math.max(0, bubble.left - mainRect.left) : 0
      const reveals = (reveal ?? [])
        .map((selector) => document.querySelector<HTMLElement>(selector))
        .flatMap((element) => (element && isVisible(element) ? [element.getBoundingClientRect()] : []))
        .map((box) => ({
          top: box.top, right: box.right, bottom: box.bottom, left: box.left, width: box.width, height: box.height,
        }))
      setLayout({
        ...(aside && paneLayout
          ? layoutForPanes(rect, paneLayout)
          : layoutFor(rect, activeStep.placement ?? 'bottom', cardHeight, width,
            controlsWithSpeaker && showSpeaker ? bubbleInset : 0)),
        reveals,
        ...(mainPane ? { mainSize: { width: mainPane.width, height: mainPane.height } } : {}),
        bubbleInset,
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
  }, [activeStep, activeTarget, aside, asideWidth, cardElement, cardWidth, controlsWithSpeaker, showSpeaker, paneLayout, reveal])

  useEffect(() => {
    if (!focusCard || !activeStep || !layoutReady) return
    const frameId = window.requestAnimationFrame(() => cardElement?.focus())
    return () => window.cancelAnimationFrame(frameId)
  }, [activeStep, cardElement, focusCard, layoutReady])

  useEffect(() => {
    if (!closeOnOutsideClick || !cardElement) return
    const { except = [] } = closeOnOutsideClick
    const closeOutside = (event: PointerEvent) => {
      const pressed = event.target
      if (!(pressed instanceof Element)) return
      if (cardElement.contains(pressed) || activeTarget?.contains(pressed)) return
      if (except.some((selector) => pressed.closest(selector))) return
      close('outside')
    }
    document.addEventListener('pointerdown', closeOutside)
    return () => document.removeEventListener('pointerdown', closeOutside)
  }, [activeTarget, cardElement, close, closeOnOutsideClick])

  const dismissible = showSkip || Boolean(closeOnOutsideClick)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (availableSteps.length === 0) return
      if (event.key === 'Escape' && dismissible) {
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
  }, [availableSteps.length, close, dismissible])

  if (!activeStep || !layout || typeof document === 'undefined') return null

  return (
    <GameplayWorkspaceTourOverlay
      markerId={markerId}
      label={label}
      finishLabel={finishLabel}
      skipLabel={skipLabel}
      showSkip={showSkip}
      skipIconOnly={skipIconOnly}
      showProgress={showProgress}
      showSpeaker={showSpeaker}
      controlsWithSpeaker={controlsWithSpeaker}
      showActions={showActions}
      finishDisabled={finishDisabled}
      cardClassName={cardClassName}
      aside={aside}
      asideWidth={asideWidth}
      paneLabels={paneLabels}
      steps={steps}
      transformable={transformable}
      activeStep={activeStep}
      activeIndex={activeIndex}
      availableSteps={availableSteps}
      layout={layout}
      collapseVector={collapseVector}
      setCardElement={setCardElement}
      setActiveIndex={setActiveIndex}
      close={close}
      transform={transform}
    />
  )
}
