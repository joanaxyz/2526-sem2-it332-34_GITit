import { useRef } from 'react'
import { Square, Trash2 } from 'lucide-react'

import type { BattleStageConfig } from '@/features/authoring/types'
import type { StageLanding } from '@/shared/battle/types'
import { cn } from '@/shared/utils/cn'

const EMPTY: BattleStageConfig = { background: null, landing: null }

/** Where a fresh land spawns: a wide ledge across the lower third of the stage. */
const DEFAULT_LANDING: StageLanding = { x: 0.06, y: 0.86, width: 0.88, height: 0.12 }
const MIN_W = 0.06
const MIN_H = 0.05
// Where fighters stand when no land is authored. Mirrors BattleStage's
// RAIL_Y_PCT (88%) so the editor's ground line matches the real battle.
const DEFAULT_RAIL_Y = 0.88

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value))
}

function clampLanding(value: StageLanding): StageLanding {
  const width = Math.min(1, Math.max(MIN_W, value.width))
  const height = Math.min(1, Math.max(MIN_H, value.height))
  return {
    x: clamp01(Math.min(value.x, 1 - width)),
    y: clamp01(Math.min(value.y, 1 - height)),
    width,
    height,
  }
}

function percentValue(value: number): number {
  return Math.round(value * 100)
}

/**
 * Author a content definition's battle land — the platform the fighters stand
 * on. The backdrop is supplied by the selected StoryWorld now (no per-content backdrop),
 * so this only places a draggable, resizable land. The preview matches the
 * in-game battle stage's proportions.
 */
export function BattleStageEditor({
  value,
  onChange,
}: {
  value: BattleStageConfig | undefined
  onChange: (config: BattleStageConfig) => void
}) {
  const config = value ?? EMPTY
  const previewRef = useRef<HTMLDivElement | null>(null)

  const landing = config.landing
  // Feet rest on the land's TOP edge (runtime uses only landing.y to place
  // fighters); show that line explicitly so authors tune the gameplay-relevant
  // coordinate, not the decorative slab height.
  const railY = landing ? landing.y : DEFAULT_RAIL_Y

  function update(next: Partial<BattleStageConfig>) {
    onChange({ ...config, ...next })
  }

  function patchLanding(patch: Partial<StageLanding>) {
    if (!landing) return
    update({ landing: clampLanding({ ...landing, ...patch }) })
  }

  function handleLandKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    if (!landing) return
    const step = event.shiftKey ? 0.05 : 0.01
    const delta: Record<string, Partial<StageLanding>> = {
      ArrowLeft: { x: landing.x - step },
      ArrowRight: { x: landing.x + step },
      ArrowUp: { y: landing.y - step },
      ArrowDown: { y: landing.y + step },
    }
    const patch = delta[event.key]
    if (!patch) return
    event.preventDefault()
    patchLanding(patch)
  }

  // Drag/resize writes normalized 0..1 rects derived from the preview box.
  function beginGesture(event: React.PointerEvent, mode: 'move' | ResizeDir) {
    if (!landing) return
    event.preventDefault()
    event.stopPropagation()
    const box = previewRef.current
    if (!box) return
    const rect = box.getBoundingClientRect()
    const startX = event.clientX
    const startY = event.clientY
    const start = landing
    ;(event.target as Element).setPointerCapture?.(event.pointerId)

    function onMove(e: PointerEvent) {
      const dx = (e.clientX - startX) / rect.width
      const dy = (e.clientY - startY) / rect.height
      update({ landing: applyGesture(start, mode, dx, dy) })
    }
    function onUp() {
      window.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
    }
    window.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
  }

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Battle stage</h2>
        <p className="author-card-sub">
          The land the fighters stand on, for every battle in this content. Drag the land to reposition it and pull its
          handles to resize. The backdrop comes from the selected StoryWorld.
        </p>
      </header>

      <div className="stage-ed-preview" ref={previewRef} aria-label="Battle stage preview">
        <div className="stage-ed-sky" aria-hidden />

        {landing ? (
          <div
            className="stage-ed-land"
            style={{
              left: `${landing.x * 100}%`,
              top: `${landing.y * 100}%`,
              width: `${landing.width * 100}%`,
              height: `${landing.height * 100}%`,
            }}
            onPointerDown={(event) => beginGesture(event, 'move')}
            onKeyDown={handleLandKeyDown}
            role="group"
            tabIndex={0}
            aria-label="Battle land. Use arrow keys to move it, or edit its numeric fields below."
          >
            <span className="stage-ed-land-label">Land</span>
            {RESIZE_DIRS.map((dir) => (
              <span
                key={dir}
                className={cn('stage-ed-land-handle', `is-${dir}`)}
                onPointerDown={(event) => beginGesture(event, dir)}
                aria-hidden
              />
            ))}
          </div>
        ) : null}

        <GroundLine railY={railY} />
      </div>

      <div className="stage-ed-section">
        <div className="stage-ed-section-head">
          <span className="author-label">Land</span>
          {landing ? (
            <button type="button" className="author-add-btn is-danger" onClick={() => update({ landing: null })}>
              <Trash2 className="size-4" aria-hidden="true" />
              Remove land
            </button>
          ) : (
            <button type="button" className="author-add-btn" onClick={() => update({ landing: DEFAULT_LANDING })}>
              <Square className="size-4" aria-hidden="true" />
              Add land
            </button>
          )}
        </div>
        <p className="author-hint">
          Fighters stand on the land's top edge — the glowing line. Y sets that ground line; width and height only size
          the decorative slab. Without a land, fighters use the stage's default rail.
        </p>
        {landing ? (
          <div className="stage-ed-field-grid" aria-label="Land transform">
            {(['x', 'y', 'width', 'height'] as const).map((key) => (
              <label className="author-field" key={key}>
                <span className="author-label">{key[0].toUpperCase()}</span>
                <input
                  className="author-input author-mono"
                  type="number"
                  min={key === 'width' ? Math.round(MIN_W * 100) : key === 'height' ? Math.round(MIN_H * 100) : 0}
                  max={100}
                  step={1}
                  value={percentValue(landing[key])}
                  onChange={(e) => patchLanding({ [key]: Number(e.target.value) / 100 })}
                />
              </label>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  )
}

/** Mirrors the runtime BattleLandingRail: the horizontal line the fighters' feet
 *  rest on (the land's top edge, `landing.y`). Pointer-transparent so it never
 *  blocks dragging the land beneath it. */
function GroundLine({ railY }: { railY: number }) {
  return (
    <div
      aria-hidden
      style={{
        position: 'absolute',
        top: `${railY * 100}%`,
        left: '50%',
        width: '82%',
        transform: 'translateX(-50%)',
        height: 0,
        borderTop: '1px dashed rgba(var(--theme-primary-rgb), 0.9)',
        boxShadow: '0 0 8px rgba(var(--theme-primary-rgb), 0.45)',
        pointerEvents: 'none',
        zIndex: 4,
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: -16,
          left: 0,
          fontSize: 10,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'rgba(var(--theme-primary-rgb), 0.9)',
          whiteSpace: 'nowrap',
        }}
      >
        Fighters stand here
      </span>
    </div>
  )
}

const RESIZE_DIRS = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'] as const
type ResizeDir = (typeof RESIZE_DIRS)[number]

/** Apply a pointer delta (normalized) to the land rect for a move or edge drag,
 *  keeping it inside the stage and above a minimum size. */
function applyGesture(start: StageLanding, mode: 'move' | ResizeDir, dx: number, dy: number): StageLanding {
  if (mode === 'move') {
    return {
      ...start,
      x: clamp01(Math.min(start.x + dx, 1 - start.width)),
      y: clamp01(Math.min(start.y + dy, 1 - start.height)),
    }
  }

  let { x, y, width, height } = start
  const right = x + width
  const bottom = y + height

  if (mode.includes('w')) {
    const nx = clamp01(Math.min(x + dx, right - MIN_W))
    width = right - nx
    x = nx
  }
  if (mode.includes('e')) {
    width = Math.max(MIN_W, Math.min(width + dx, 1 - x))
  }
  if (mode.includes('n')) {
    const ny = clamp01(Math.min(y + dy, bottom - MIN_H))
    height = bottom - ny
    y = ny
  }
  if (mode.includes('s')) {
    height = Math.max(MIN_H, Math.min(height + dy, 1 - y))
  }
  return { x, y, width, height }
}
