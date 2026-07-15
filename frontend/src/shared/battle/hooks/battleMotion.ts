export const TRAVEL_SCROLL_PX = 460
export const TRAVEL_SCROLL_MS = 1100
export const RUN_IN_SCROLL_MIN_PX = 160
export const RUN_IN_SCROLL_SCALE = 0.72
export const CENTER_SCROLL_FRAC = 0.38
export const CENTER_SCROLL_MS = 820
// Fraction of Blue's closing run the camera drifts to follow him (0 = static
// camera, 1 = fully locked on Blue). A partial follow keeps him advancing on
// screen while the world visibly pans past.
export const CAMERA_FOLLOW_FRAC = 0.5
export const MONSTER_PEEK_MS = 540
export const MONSTER_ENTRY_STAGGER_MS = 100
export const SIGHTED_IDLE_PAUSE_MS = 180
export const MONSTER_PEEK_VISIBLE = 0.42
export const PEEK_START_FRAC = 0.52
const MISS_FLOOR_EDGE_PADDING_PX = 32
const MISS_FLOOR_MIN_PLAYER_ADVANCE_PX = 64
const MISS_FLOOR_MAX_PLAYER_ADVANCE_PX = 150
const MISS_FLOOR_MIN_ENEMY_CLEARANCE_PX = 176
const MISS_FLOOR_PLAYER_BIAS = 0.32

export type RectLike = Pick<DOMRectReadOnly, 'left' | 'right' | 'top' | 'bottom' | 'width' | 'height'>

export function readTranslateX(node: HTMLElement): number {
  const inline = node.style.transform
  const match = /translate(?:X)?\(([-\d.]+)px/.exec(inline)
  if (match) return Number(match[1])
  const matrix = window.getComputedStyle(node).transform
  if (matrix && matrix !== 'none') {
    const parts = matrix.match(/matrix\(([^)]+)\)/)
    if (parts) {
      const values = parts[1].split(',').map((v) => Number.parseFloat(v.trim()))
      if (values.length === 6) return values[4]
    }
  }
  return 0
}

export function prefersReducedMotion(): boolean {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function boundedAnimation(promise: Promise<void>, ms: number): Promise<void> {
  return Promise.race([
    promise,
    new Promise<void>((resolve) => {
      window.setTimeout(resolve, ms)
    }),
  ])
}

export function wait(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

export function nextPaint(): Promise<void> {
  return new Promise((resolve) => {
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      resolve()
    }
    requestAnimationFrame(finish)
    window.setTimeout(finish, 80)
  })
}

export function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value))
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export function parseBattleRailY(stage: HTMLElement | null, layerBox: RectLike): number | null {
  if (!stage) return null
  const style = window.getComputedStyle(stage)
  const raw = style.getPropertyValue('--battle-rail-y').trim()
  const value = Number.parseFloat(raw)
  if (!Number.isFinite(value)) return null
  const stageBox = stage.getBoundingClientRect()
  if (raw.endsWith('%')) return stageBox.top + stageBox.height * (value / 100) - layerBox.top
  if (raw.endsWith('px')) return stageBox.top + value - layerBox.top
  return null
}

export function missedSpellFloorTarget({
  layerBox,
  playerBox,
  enemyBox,
  floorY,
}: {
  layerBox: RectLike
  playerBox: RectLike
  enemyBox: RectLike
  floorY?: number | null
}): { x: number; y: number } {
  const playerFrontX = playerBox.left + playerBox.width * 0.82 - layerBox.left
  const enemyLeftX = enemyBox.left - layerBox.left
  const enemyClearance = Math.max(MISS_FLOOR_MIN_ENEMY_CLEARANCE_PX, enemyBox.width * 0.72)
  const maxXBeforeEnemy = enemyLeftX - enemyClearance
  const gapBeforeEnemy = Math.max(0, maxXBeforeEnemy - playerFrontX)
  const preferredAdvance = clamp(
    gapBeforeEnemy * MISS_FLOOR_PLAYER_BIAS,
    MISS_FLOOR_MIN_PLAYER_ADVANCE_PX,
    MISS_FLOOR_MAX_PLAYER_ADVANCE_PX,
  )
  const preferredX = playerFrontX + preferredAdvance
  const stageMinX = MISS_FLOOR_EDGE_PADDING_PX
  const stageMaxX = Math.max(stageMinX, layerBox.width - MISS_FLOOR_EDGE_PADDING_PX)
  const upperX = Math.min(stageMaxX, maxXBeforeEnemy)
  const lowerX = Math.min(Math.max(stageMinX, playerFrontX + MISS_FLOOR_MIN_PLAYER_ADVANCE_PX), upperX)
  const fallbackFloorY = Math.max(playerBox.bottom, enemyBox.bottom) - layerBox.top

  return {
    x: clamp(preferredX, lowerX, upperX),
    y: clamp(floorY ?? fallbackFloorY, 0, Math.max(0, layerBox.height - 8)),
  }
}
