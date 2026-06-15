import type { TowerArtifactRole, TowerPieceType } from '@/shared/assets/types'

export function pieceIdFromInstance(instanceId: string): number | null {
  const match = /-piece-(\d+)$/.exec(instanceId)
  return match ? Number(match[1]) : null
}

export const PIECE_TYPE_LABEL: Record<TowerPieceType, string> = {
  crown: 'Crown',
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

/** A piece's free transform, normalized to concrete numbers. */
export type PieceTransform = { x: number; y: number; scale: number; rotation: number }

/** A staged artifact tweak - only the fields the user changed are present. */
export type ArtifactEdit = {
  x?: number
  y?: number
  scale?: number
  rotation?: number
  width?: number
  height?: number
}

export type ArtifactTransform = {
  x: number
  y: number
  scale: number
  rotation: number
  width: number
  height: number
}

export const IDENTITY_PIECE_TRANSFORM: PieceTransform = { x: 0, y: 0, scale: 1, rotation: 0 }

export const PIECE_SCALE_RANGE = { min: 0.2, max: 2.5 } as const
export const PIECE_ROTATION_RANGE = { min: -180, max: 180 } as const
export const ARTIFACT_SCALE_RANGE = { min: 0.25, max: 3 } as const
export const ARTIFACT_ROTATION_RANGE = { min: -180, max: 180 } as const

export function readPieceTransform(transform: Record<string, unknown> | null | undefined): PieceTransform {
  return {
    x: finiteNumber(transform?.x) ?? 0,
    y: finiteNumber(transform?.y) ?? 0,
    scale: positiveNumber(transform?.scale) ?? 1,
    rotation: finiteNumber(transform?.rotation) ?? finiteNumber(transform?.rotate) ?? 0,
  }
}

export function pieceTransformIsIdentity(transform: PieceTransform): boolean {
  return transform.x === 0 && transform.y === 0 && transform.scale === 1 && transform.rotation === 0
}

export function pieceTransformsEqual(a: PieceTransform, b: PieceTransform): boolean {
  return a.x === b.x && a.y === b.y && a.scale === b.scale && a.rotation === b.rotation
}

/** Identity transforms serialize to `{}` so the backend stores a clean slot. */
export function pieceTransformToRecord(transform: PieceTransform): Record<string, number> {
  if (pieceTransformIsIdentity(transform)) return {}
  return { x: transform.x, y: transform.y, scale: transform.scale, rotation: transform.rotation }
}

export function readArtifactTransform(
  artifact: {
    x: number
    y: number
    scale: number
    rotation: number
    width: number
    height: number
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
  }
}

export function clampNumber(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
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
