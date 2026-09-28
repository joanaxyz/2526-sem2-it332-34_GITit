import { ArrowLeft, ArrowRight, Check, GripHorizontal, MoveDiagonal2, RotateCcw, X } from 'lucide-react'
import type { CSSProperties, Dispatch, ReactNode, SetStateAction } from 'react'
import { createPortal } from 'react-dom'

import { Button } from '@/shared/components/Button'

import {
  DESKTOP_CARD_WIDTH,
  HEADER_CLEARANCE,
  connectorPathFor,
  spotlightRect,
  VIEWPORT_GAP,
} from './gameplayWorkspaceTourLayout'
import type {
  CollapseVector,
  MeasuredWorkspaceTourLayout,
  ResolvedWorkspaceTourStep,
  WorkspaceTourCloseReason,
  WorkspaceTourPane as Pane,
  WorkspaceTourPosition as Position,
  WorkspaceTourStep,
} from './gameplayWorkspaceTourTypes'
import {
  workspaceTourFrame,
  type WorkspaceTourTransform,
} from './useWorkspaceTourTransform'

const ASIDE_GAP = 12

export function GameplayWorkspaceTourOverlay({
  markerId,
  label,
  finishLabel,
  skipLabel,
  showSkip,
  skipIconOnly,
  showProgress,
  showActions,
  finishDisabled,
  cardClassName,
  aside,
  asideWidth,
  paneLabels,
  steps,
  transformable,
  activeStep,
  activeIndex,
  availableSteps,
  layout,
  collapseVector,
  setCardElement,
  setActiveIndex,
  close,
  transform,
}: {
  markerId: string
  label: string
  finishLabel: string
  skipLabel: string
  showSkip: boolean
  skipIconOnly: boolean
  showProgress: boolean
  showActions: boolean
  finishDisabled: boolean
  cardClassName?: string
  aside?: ReactNode
  asideWidth: number
  paneLabels: Record<Pane, string>
  steps: readonly WorkspaceTourStep[]
  transformable: boolean
  activeStep: WorkspaceTourStep
  activeIndex: number
  availableSteps: readonly ResolvedWorkspaceTourStep[]
  layout: MeasuredWorkspaceTourLayout
  collapseVector: CollapseVector | null
  setCardElement: Dispatch<SetStateAction<HTMLElement | null>>
  setActiveIndex: Dispatch<SetStateAction<number>>
  close: (reason: WorkspaceTourCloseReason) => void
  transform: WorkspaceTourTransform
}) {
  const {
    panePositions,
    paneSizes,
    frontPane,
    setFrontPane,
    transformMode,
    transformed,
    resetTransform,
    beginMove,
    beginResize,
    moveWithKeyboard,
    resizeWithKeyboard,
  } = transform
  const separate = Boolean(aside)
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  // Until the learner moves one, the cards sit side by side where layout put them.
  const mainWidth = paneSizes.main?.width ?? (separate ? DESKTOP_CARD_WIDTH : layout.card.width)
  const autoPositions: Record<Pane, Position> = {
    main: layout.card,
    aside: { left: layout.card.left + mainWidth + ASIDE_GAP, top: layout.card.top },
  }
  const positionOf = (pane: Pane) => panePositions[pane] ?? autoPositions[pane]
  const mainFrame = workspaceTourFrame(positionOf('main'), paneSizes.main ?? layout.mainSize ?? layout.card)
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
