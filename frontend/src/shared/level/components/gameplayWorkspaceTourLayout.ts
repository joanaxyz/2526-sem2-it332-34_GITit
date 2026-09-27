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
  /** Extra regions left undimmed so the learner can still read them. */
  reveals?: RectSnapshot[]
  /** Height the card must stay within to sit beside its target without covering it. */
  room?: number | null
}

export const VIEWPORT_GAP = 16
const TARGET_GAP = 18
const TARGET_PADDING = 9
export const HEADER_CLEARANCE = 76
export const DEFAULT_CARD_HEIGHT = 236
export const DESKTOP_CARD_WIDTH = 352
const NARROW_VIEWPORT = 420
const OVERLAP_PENALTY = 100000
// Below this, capping the card would leave too little to read; let placement fall back.
const MIN_ROOM = 200

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

function clampIntoViewport(
  left: number,
  top: number,
  width: number,
  height: number,
  viewportWidth: number,
  viewportHeight: number,
): RectSnapshot {
  const maxLeft = Math.max(VIEWPORT_GAP, viewportWidth - width - VIEWPORT_GAP)
  const maxTop = Math.max(VIEWPORT_GAP, viewportHeight - height - VIEWPORT_GAP)
  return cardRect(
    Math.min(Math.max(left, VIEWPORT_GAP), maxLeft),
    Math.min(Math.max(top, VIEWPORT_GAP), maxTop),
    width,
    height,
  )
}

/** Distance from the target, penalising placements that cover it. */
function placementCost(card: RectSnapshot, target: RectSnapshot) {
  const covers = !(
    card.right <= target.left ||
    card.left >= target.right ||
    card.bottom <= target.top ||
    card.top >= target.bottom
  )
  const dx = card.left + card.width / 2 - (target.left + target.width / 2)
  const dy = card.top + card.height / 2 - (target.top + target.height / 2)
  return Math.hypot(dx, dy) + (covers ? OVERLAP_PENALTY : 0)
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
  preferredWidth: number = DESKTOP_CARD_WIDTH,
): TourLayout {
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const available = viewportWidth - VIEWPORT_GAP * 2
  // On phones the card takes the full gutter width so it sits symmetrically
  // rather than being clamped against one edge.
  const cardWidth = available <= NARROW_VIEWPORT ? available : Math.min(preferredWidth, available)
  const target = rectSnapshot(targetRect)
  // Above or below the target, a tall card is capped to the space there (its
  // content scrolls) instead of being pushed over the thing it explains. The
  // cap depends only on the target, so re-measuring the capped card is stable.
  const space =
    preferredPlacement === 'top'
      ? target.top - TARGET_GAP - VIEWPORT_GAP
      : preferredPlacement === 'bottom'
        ? viewportHeight - target.bottom - TARGET_GAP - VIEWPORT_GAP
        : null
  const room = space !== null && space >= MIN_ROOM ? Math.floor(space) : null
  const cardHeight = Math.min(
    measuredCardHeight || DEFAULT_CARD_HEIGHT,
    room ?? Number.POSITIVE_INFINITY,
    viewportHeight - VIEWPORT_GAP * 2,
  )
  const placements = [preferredPlacement, 'bottom', 'top', 'right', 'left'].filter(
    (placement, index, items) => items.indexOf(placement) === index,
  ) as WorkspaceTourPlacement[]

  let card: RectSnapshot | null = null
  for (const placement of placements) {
    const candidate = candidateFor(placement, target, cardWidth, cardHeight)
    const nextCard = cardRect(candidate.left, candidate.top, cardWidth, cardHeight)
    if (cardFits(nextCard, target, viewportWidth, viewportHeight)) {
      card = nextCard
      break
    }
  }

  // Nothing fits outright - a short viewport, or a card taller than the space
  // beside its target. Clamp each placement into view and keep the one nearest
  // the target, so the card stays beside what it explains instead of landing in
  // a corner and dragging the connector across the whole workspace.
  card ??= placements
    .map((placement) => {
      const candidate = candidateFor(placement, target, cardWidth, cardHeight)
      const clamped = clampIntoViewport(
        candidate.left,
        candidate.top,
        cardWidth,
        cardHeight,
        viewportWidth,
        viewportHeight,
      )
      return { card: clamped, cost: placementCost(clamped, target) }
    })
    .reduce((best, option) => (option.cost < best.cost ? option : best)).card

  const { start, end } = connectorPoints(card, target)
  const control = {
    x: start.x + (end.x - start.x) * 0.54,
    y: start.y + (end.y - start.y) * 0.38,
  }

  return {
    target,
    card,
    arrowPath: `M ${start.x} ${start.y} Q ${control.x} ${control.y} ${end.x} ${end.y}`,
    room,
  }
}

export function spotlightRect(
  target: RectSnapshot,
  viewportWidth: number,
  viewportHeight: number,
  padding = TARGET_PADDING,
) {
  const left = Math.max(0, target.left - padding)
  const top = Math.max(0, target.top - padding)
  const right = Math.min(viewportWidth, target.right + padding)
  const bottom = Math.min(viewportHeight, target.bottom + padding)
  return { left, top, right, bottom, width: right - left, height: bottom - top }
}

export function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}
