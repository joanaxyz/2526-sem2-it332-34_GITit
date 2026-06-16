import { describe, expect, it } from 'vitest'

import {
  handleSigns,
  readPieceTransform,
  pieceTransformToRecord,
  resizeBoxFromHandle,
  rotateVec,
  type ResizeHandle,
} from './editorUtils'

/** Corner of a centred, rotated box in world space, for the given handle. */
function cornerOf(
  handle: ResizeHandle,
  box: { w: number; h: number; cx: number; cy: number },
  rotation: number,
) {
  const { sx, sy } = handleSigns(handle)
  const local = { x: (sx * box.w) / 2, y: (sy * box.h) / 2 }
  const rotated = rotateVec(local, rotation)
  return { x: box.cx + rotated.x, y: box.cy + rotated.y }
}

const OPPOSITE: Record<ResizeHandle, ResizeHandle> = {
  nw: 'se',
  n: 's',
  ne: 'sw',
  e: 'w',
  se: 'nw',
  s: 'n',
  sw: 'ne',
  w: 'e',
}

describe('rotateVec', () => {
  it('rotates 90 degrees clockwise (y-down)', () => {
    const r = rotateVec({ x: 1, y: 0 }, 90)
    expect(r.x).toBeCloseTo(0, 6)
    expect(r.y).toBeCloseTo(1, 6)
  })
})

describe('resizeBoxFromHandle', () => {
  const start = { w0: 100, h0: 60, cx: 200, cy: 150 }

  it('grows width and height from the SE corner with NW pinned', () => {
    const box = resizeBoxFromHandle({
      handle: 'se',
      rotation: 0,
      local: { x: 40, y: 20 },
      ...start,
      minW: 6,
      minH: 6,
    })
    expect(box.w).toBe(140)
    expect(box.h).toBe(80)
    // Centre shifts by half the growth toward the dragged corner.
    expect(box.cx).toBe(220)
    expect(box.cy).toBe(160)
  })

  it.each<ResizeHandle>(['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'])(
    'keeps the opposite handle pinned for %s (rotation 0)',
    (handle) => {
      const anchorBefore = cornerOf(OPPOSITE[handle], { ...start, w: start.w0, h: start.h0 }, 0)
      const box = resizeBoxFromHandle({
        handle,
        rotation: 0,
        local: { x: 24, y: -18 },
        ...start,
        minW: 6,
        minH: 6,
      })
      const anchorAfter = cornerOf(OPPOSITE[handle], box, 0)
      expect(anchorAfter.x).toBeCloseTo(anchorBefore.x, 6)
      expect(anchorAfter.y).toBeCloseTo(anchorBefore.y, 6)
    },
  )

  it('keeps the opposite corner pinned under rotation', () => {
    const rotation = 37
    const anchorBefore = cornerOf('nw', { ...start, w: start.w0, h: start.h0 }, rotation)
    const box = resizeBoxFromHandle({
      handle: 'se',
      rotation,
      local: { x: 30, y: 22 },
      ...start,
      minW: 6,
      minH: 6,
    })
    const anchorAfter = cornerOf('nw', box, rotation)
    expect(anchorAfter.x).toBeCloseTo(anchorBefore.x, 6)
    expect(anchorAfter.y).toBeCloseTo(anchorBefore.y, 6)
  })

  it('only touches one axis for an edge handle', () => {
    const box = resizeBoxFromHandle({
      handle: 'e',
      rotation: 0,
      local: { x: 30, y: 999 },
      ...start,
      minW: 6,
      minH: 6,
    })
    expect(box.w).toBe(130)
    expect(box.h).toBe(60)
  })

  it('preserves aspect ratio when keepAspect is set on a corner', () => {
    const box = resizeBoxFromHandle({
      handle: 'se',
      rotation: 0,
      local: { x: 50, y: 0 },
      ...start,
      minW: 6,
      minH: 6,
      keepAspect: true,
    })
    expect(box.w / box.h).toBeCloseTo(start.w0 / start.h0, 6)
  })

  it('clamps to the minimum size', () => {
    const box = resizeBoxFromHandle({
      handle: 'se',
      rotation: 0,
      local: { x: -500, y: -500 },
      ...start,
      minW: 6,
      minH: 6,
    })
    expect(box.w).toBe(6)
    expect(box.h).toBe(6)
  })
})

describe('piece transform serialization', () => {
  it('reads a legacy uniform scale into both axes', () => {
    const t = readPieceTransform({ x: 4, y: 8, scale: 1.5, rotation: 10 })
    expect(t.scaleX).toBe(1.5)
    expect(t.scaleY).toBe(1.5)
  })

  it('round-trips per-axis scale and mirrors `scale` only when uniform', () => {
    const stretched = pieceTransformToRecord({ x: 0, y: 0, scaleX: 2, scaleY: 0.5, rotation: 0 })
    expect(stretched.scaleX).toBe(2)
    expect(stretched.scaleY).toBe(0.5)
    expect(stretched.scale).toBeUndefined()

    const uniform = pieceTransformToRecord({ x: 0, y: 0, scaleX: 1.25, scaleY: 1.25, rotation: 0 })
    expect(uniform.scale).toBe(1.25)
  })

  it('serializes the identity transform to an empty record', () => {
    expect(pieceTransformToRecord({ x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0 })).toEqual({})
  })
})
