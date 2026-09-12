export type WorkspaceTourPlacement = 'top' | 'right' | 'bottom' | 'left'

export type RectSnapshot = {
  top: number
  right: number
  bottom: number
  left: number
  width: number
  height: number
}

type Point = { x: number; y: number }

export type TourLayout = {
  target: RectSnapshot
  card: RectSnapshot
  arrowPath: string
}

export const VIEWPORT_GAP = 16
const TARGET_GAP = 18
const TARGET_PADDING = 9
export const HEADER_CLEARANCE = 76
export const DEFAULT_CARD_HEIGHT = 236
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

export function layoutFor(
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

export function spotlightRect(target: RectSnapshot, viewportWidth: number, viewportHeight: number) {
  const left = Math.max(0, target.left - TARGET_PADDING)
  const top = Math.max(0, target.top - TARGET_PADDING)
  const right = Math.min(viewportWidth, target.right + TARGET_PADDING)
  const bottom = Math.min(viewportHeight, target.bottom + TARGET_PADDING)
  return { left, top, right, bottom, width: right - left, height: bottom - top }
}

export function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}
