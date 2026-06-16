import type { TowerArtifactRole, TowerPieceType } from '@/shared/assets/types'

export function pieceIdFromInstance(instanceId: string): number | null {
  const match = /-piece-(\d+)$/.exec(instanceId)
  return match ? Number(match[1]) : null
}

export const PIECE_TYPE_LABEL: Record<TowerPieceType, string> = {
  crown: 'Crown',
  base: 'Base',
  section: 'Section',
  landing: 'Landing',
}

export const ARTIFACT_ROLE_LABEL: Record<TowerArtifactRole, string> = {
  normal: 'Normal artifact',
  adventure: 'Adventure artifact',
  challenge: 'Challenge artifact',
  tome: 'Tome artifact',
}

export const INTERACTABLE_ROLES: TowerArtifactRole[] = ['adventure', 'challenge', 'tome']

/** A piece's free transform, normalized to concrete numbers. Scale is per-axis
 *  (scaleX/scaleY) so pieces can be stretched, not only scaled uniformly. */
export type PieceTransform = { x: number; y: number; scaleX: number; scaleY: number; rotation: number; zIndex: number }

/** A staged artifact tweak - only the fields the user changed are present. */
export type ArtifactEdit = {
  targetInstanceId?: string
  x?: number
  y?: number
  scale?: number
  rotation?: number
  width?: number
  height?: number
  zIndex?: number
}

export type ArtifactTransform = {
  x: number
  y: number
  scale: number
  rotation: number
  width: number
  height: number
  zIndex: number
}

export const IDENTITY_PIECE_TRANSFORM: PieceTransform = { x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0, zIndex: 0 }

export const PIECE_SCALE_RANGE = { min: 0.2, max: 2.5 } as const
export const PIECE_ROTATION_RANGE = { min: -180, max: 180 } as const
export const ARTIFACT_SCALE_RANGE = { min: 0.25, max: 3 } as const
export const ARTIFACT_ROTATION_RANGE = { min: -180, max: 180 } as const

export function readPieceTransform(transform: Record<string, unknown> | null | undefined): PieceTransform {
  // Legacy slots stored a single uniform `scale`; read it as both axes so old
  // designs keep rendering identically after the per-axis upgrade.
  const legacy = positiveNumber(transform?.scale)
  return {
    x: finiteNumber(transform?.x) ?? 0,
    y: finiteNumber(transform?.y) ?? 0,
    scaleX: positiveNumber(transform?.scaleX) ?? legacy ?? 1,
    scaleY: positiveNumber(transform?.scaleY) ?? legacy ?? 1,
    rotation: finiteNumber(transform?.rotation) ?? finiteNumber(transform?.rotate) ?? 0,
    zIndex: finiteNumber(transform?.zIndex) ?? 0,
  }
}

export function pieceTransformIsIdentity(transform: PieceTransform): boolean {
  return (
    transform.x === 0 &&
    transform.y === 0 &&
    transform.scaleX === 1 &&
    transform.scaleY === 1 &&
    transform.rotation === 0 &&
    transform.zIndex === 0
  )
}

export function pieceTransformIsUniform(transform: PieceTransform): boolean {
  return transform.scaleX === transform.scaleY
}

export function pieceTransformsEqual(a: PieceTransform, b: PieceTransform): boolean {
  return (
    a.x === b.x &&
    a.y === b.y &&
    a.scaleX === b.scaleX &&
    a.scaleY === b.scaleY &&
    a.rotation === b.rotation &&
    a.zIndex === b.zIndex
  )
}

/** Identity transforms serialize to `{}` so the backend stores a clean slot.
 *  A `scale` mirror is written when the two axes are equal, so any consumer that
 *  still reads the legacy uniform field stays correct. */
export function pieceTransformToRecord(transform: PieceTransform): Record<string, number> {
  if (pieceTransformIsIdentity(transform)) return {}
  const record: Record<string, number> = {
    x: transform.x,
    y: transform.y,
    scaleX: transform.scaleX,
    scaleY: transform.scaleY,
    rotation: transform.rotation,
    zIndex: transform.zIndex,
  }
  if (transform.scaleX === transform.scaleY) record.scale = transform.scaleX
  return record
}

export function readArtifactTransform(
  artifact: {
    x: number
    y: number
    scale: number
    rotation: number
    width: number
    height: number
    zIndex: number
  },
  edit?: ArtifactEdit,
): ArtifactTransform {
  return {
    x: finiteNumber(edit?.x) ?? artifact.x,
    y: finiteNumber(edit?.y) ?? artifact.y,
    scale: positiveNumber(edit?.scale) ?? artifact.scale,
    rotation: finiteNumber(edit?.rotation) ?? artifact.rotation,
    width: positiveNumber(edit?.width) ?? artifact.width,
    height: positiveNumber(edit?.height) ?? artifact.height,
    zIndex: finiteNumber(edit?.zIndex) ?? artifact.zIndex,
  }
}

export function clampNumber(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

// --- Transform-box geometry -------------------------------------------------
// Shared by the on-canvas resize gizmos for pieces and artifacts. Both render a
// box centred on its position, scaled, then rotated; resizing has to keep the
// handle opposite the one being dragged pinned in place.

export type Vec2 = { x: number; y: number }

/** Rotate a vector by `deg` degrees (clockwise in screen space, y-down). */
export function rotateVec(v: Vec2, deg: number): Vec2 {
  const rad = (deg * Math.PI) / 180
  const cos = Math.cos(rad)
  const sin = Math.sin(rad)
  return { x: v.x * cos - v.y * sin, y: v.x * sin + v.y * cos }
}

export type ResizeHandle = 'nw' | 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w'

/** Which box edges a handle drives: -1 = min side, +1 = max side, 0 = fixed. */
const HANDLE_SIGNS: Record<ResizeHandle, { sx: number; sy: number }> = {
  nw: { sx: -1, sy: -1 },
  n: { sx: 0, sy: -1 },
  ne: { sx: 1, sy: -1 },
  e: { sx: 1, sy: 0 },
  se: { sx: 1, sy: 1 },
  s: { sx: 0, sy: 1 },
  sw: { sx: -1, sy: 1 },
  w: { sx: -1, sy: 0 },
}

export function handleSigns(handle: ResizeHandle): { sx: number; sy: number } {
  return HANDLE_SIGNS[handle]
}

/**
 * Resize a centred, rotated box by dragging one handle while the opposite one
 * stays put. Everything is in the caller's own "displayed" units; `local` is the
 * pointer delta already rotated into the box's un-rotated frame (x along width,
 * y along height). Returns the new displayed size and the shifted centre, which
 * the caller maps back onto its own model fields.
 */
export function resizeBoxFromHandle(opts: {
  handle: ResizeHandle
  rotation: number
  local: Vec2
  w0: number
  h0: number
  cx: number
  cy: number
  minW: number
  minH: number
  keepAspect?: boolean
}): { w: number; h: number; cx: number; cy: number } {
  const { handle, rotation, local, w0, h0, cx, cy, minW, minH, keepAspect } = opts
  const { sx, sy } = HANDLE_SIGNS[handle]
  let w = Math.max(minW, w0 + sx * local.x)
  let h = Math.max(minH, h0 + sy * local.y)
  if (keepAspect && sx !== 0 && sy !== 0 && w0 > 0 && h0 > 0) {
    const fx = w / w0
    const fy = h / h0
    const f = Math.abs(fx - 1) >= Math.abs(fy - 1) ? fx : fy
    w = Math.max(minW, w0 * f)
    h = Math.max(minH, h0 * f)
  }
  const shift = rotateVec({ x: (sx * (w - w0)) / 2, y: (sy * (h - h0)) / 2 }, rotation)
  return { w, h, cx: cx + shift.x, cy: cy + shift.y }
}

export function roundTo(value: number, decimals: number): number {
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}

function finiteNumber(value: unknown): number | null {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function positiveNumber(value: unknown): number | null {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}
