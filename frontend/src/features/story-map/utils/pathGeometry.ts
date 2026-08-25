export type PathPoint = { x: number; y: number }

/* Path geometry lives in pixels, not percentages: a fixed vertical rhythm
   keeps nodes readable at ANY level count (the stage grows and the page
   scrolls), and the SVG shares the same pixel space so the dashed route
   passes exactly through every node with an undistorted stroke. */
const PATH_STEP = 118
const PATH_TOP = 78
const PATH_BOTTOM = 96
const TRIAL_CARD_H = 86
const TRIAL_CARD_GAP = 17
const TRIAL_FLYOUT_W = 262

export function pathGeometry(count: number, width: number) {
  const amp = Math.max(56, Math.min(112, width * 0.5 - 176))
  const cx = Math.max(amp + 64, Math.min(width * 0.38, 300))
  const points: PathPoint[] = Array.from({ length: count }, (_, index) => ({
    x: cx + amp * Math.sin(index * 0.85),
    y: PATH_TOP + index * PATH_STEP,
  }))
  const height = count > 0 ? PATH_TOP + (count - 1) * PATH_STEP + PATH_BOTTOM : 0
  return { points, height }
}

/** Smooth Catmull-Rom-to-Bezier spline through arbitrary points, so the
 *  route line always reaches every node regardless of how many there are. */
export function pathDataFor(points: PathPoint[]): string {
  if (points.length < 2) return ''
  const at = (index: number) => points[Math.min(Math.max(index, 0), points.length - 1)]
  let d = `M${points[0].x} ${points[0].y}`
  for (let index = 0; index < points.length - 1; index += 1) {
    const p0 = at(index - 1)
    const p1 = at(index)
    const p2 = at(index + 1)
    const p3 = at(index + 2)
    const c1x = p1.x + (p2.x - p0.x) / 6
    const c1y = p1.y + (p2.y - p0.y) / 6
    const c2x = p2.x - (p3.x - p1.x) / 6
    const c2y = p2.y - (p3.y - p1.y) / 6
    d += ` C${c1x} ${c1y} ${c2x} ${c2y} ${p2.x} ${p2.y}`
  }
  return d
}

/** Anchor for the trials flyout beside the challenge node, clamped inside
 *  the canvas. */
export function trialFlyoutPlacement(trialPoint: PathPoint, width: number, height: number) {
  const flyoutHeight = TRIAL_CARD_H * 3 + TRIAL_CARD_GAP * 2
  const left = Math.min(trialPoint.x + 92, width - TRIAL_FLYOUT_W - 8)
  const top = Math.max(8, Math.min(trialPoint.y - flyoutHeight / 2, height - flyoutHeight - 8))
  const connectors = [0, 1, 2].map((index) => {
    const endY = top + TRIAL_CARD_H / 2 + index * (TRIAL_CARD_H + TRIAL_CARD_GAP)
    const startX = trialPoint.x + 38
    return `M${startX} ${trialPoint.y} C${startX + 48} ${trialPoint.y}, ${left - 46} ${endY}, ${left + 4} ${endY}`
  })
  return { left, top, connectors }
}
