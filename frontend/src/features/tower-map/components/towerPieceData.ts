import type {
  TowerLayoutDescriptor,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'

/** First layout piece of a given structural type (spire, landing, …). */
export function pieceByType(
  layout: TowerLayoutDescriptor | null,
  pieceType: TowerLayoutPieceDescriptor['pieceType'],
) {
  return layout?.pieces.find((piece) => piece.pieceType === pieceType) ?? null
}

/** Layout piece whose instanceId ends with a suffix (e.g. `landing-after-adventure`). */
export function pieceBySuffix(layout: TowerLayoutDescriptor | null, suffix: string) {
  return layout?.pieces.find((piece) => piece.instanceId.endsWith(suffix)) ?? null
}

/**
 * The render variant for a layout piece. For landings this is derived from
 * *position* — which section the landing caps — not from the instanceId, so it
 * is correct for both live storeys (semantic instanceIds) and saved tower
 * designs (numeric `…-piece-<n>` instanceIds). Returns `undefined` for pieces
 * that have no variant (e.g. the tome lectern / a door artifact).
 */
export function pieceVariant(
  layout: TowerLayoutDescriptor | null,
  piece: TowerLayoutPieceDescriptor,
): string | undefined {
  switch (piece.pieceType) {
    case 'spire':
      return 'roof'
    case 'window_section':
      return 'regular'
    case 'adventure_section':
      return 'adventure'
    case 'challenge_section':
      return 'challenge'
    case 'landing':
      return landingVariant(layout, piece)
    default:
      return undefined
  }
}

/** A landing's variant is decided by the nearest non-landing piece above it. */
function landingVariant(layout: TowerLayoutDescriptor | null, piece: TowerLayoutPieceDescriptor) {
  const pieces = layout?.pieces ?? []
  const index = pieces.findIndex((entry) => entry.instanceId === piece.instanceId)
  for (let i = index - 1; i >= 0; i--) {
    const type = pieces[i].pieceType
    if (type === 'landing') continue
    if (type === 'challenge_section') return 'after-challenges'
    if (type === 'tome') return 'tome'
    return 'regular'
  }
  return 'regular'
}

export function towerDescriptorFor(
  piece: TowerLayoutPieceDescriptor | null | undefined,
  descriptors: Record<string, TowerPieceAssetDescriptor>,
) {
  return piece ? descriptors[piece.assetSlug] ?? null : null
}

export function towerPieceAttrs(
  piece: TowerLayoutPieceDescriptor | null | undefined,
  descriptor?: TowerPieceAssetDescriptor | null,
  options?: { variant?: string },
) {
  const rail = walkRailAnchor(descriptor, options?.variant)
  const viewBox = pieceViewBox(descriptor, options?.variant)
  const safeBounds = artifactSafeBounds(descriptor, options?.variant)
  return {
    'data-piece-id': piece?.instanceId,
    'data-asset-slug': piece?.assetSlug,
    'data-piece-type': piece?.pieceType,
    'data-piece-variant': options?.variant,
    'data-viewbox-x': viewBox.x,
    'data-viewbox-y': viewBox.y,
    'data-viewbox-width': viewBox.width,
    'data-viewbox-height': viewBox.height,
    'data-walk-rail-x1': rail?.x1,
    'data-walk-rail-y1': rail?.y1,
    'data-walk-rail-x2': rail?.x2,
    'data-walk-rail-y2': rail?.y2,
    'data-artifact-safe-x': safeBounds?.x,
    'data-artifact-safe-y': safeBounds?.y,
    'data-artifact-safe-width': safeBounds?.width,
    'data-artifact-safe-height': safeBounds?.height,
  }
}

/** Whether a piece asset carries a valid walk_rail anchor, i.e. Blue can stand on it. */
export function pieceHasWalkRail(descriptor?: TowerPieceAssetDescriptor | null) {
  return walkRailAnchor(descriptor) !== null
}

export function walkRailAnchor(descriptor?: TowerPieceAssetDescriptor | null, variant?: string) {
  const detail = variantDetail(descriptor, variant)
  const rail = detail.anchors.walk_rail
  if (!isRecord(rail)) return null
  const x1 = finiteNumber(rail.x1)
  const y1 = finiteNumber(rail.y1)
  const x2 = finiteNumber(rail.x2)
  const y2 = finiteNumber(rail.y2)
  if ([x1, y1, x2, y2].some((value) => value === null)) return null
  return { x1, y1, x2, y2 }
}

export function pieceViewBox(descriptor?: TowerPieceAssetDescriptor | null, variant?: string) {
  return parseViewBox(variantDetail(descriptor, variant).viewBox)
}

export function pieceViewBoxString(descriptor?: TowerPieceAssetDescriptor | null, variant?: string) {
  const box = pieceViewBox(descriptor, variant)
  return `${box.x} ${box.y} ${box.width} ${box.height}`
}

export function artifactSafeBounds(descriptor?: TowerPieceAssetDescriptor | null, variant?: string) {
  const detail = variantDetail(descriptor, variant)
  const safe = isRecord(detail.bounds.artifact_safe_bounds) ? detail.bounds.artifact_safe_bounds : detail.bounds
  const x = finiteNumber(safe.x)
  const y = finiteNumber(safe.y)
  const width = positiveNumber(safe.width)
  const height = positiveNumber(safe.height)
  if (x === null || y === null || width === null || height === null) return null
  return { x, y, width, height }
}

export function clientPointToPiecePoint(
  clientX: number,
  clientY: number,
  element: HTMLElement,
  descriptor?: TowerPieceAssetDescriptor | null,
  variant?: string,
) {
  const rect = element.getBoundingClientRect()
  const box = pieceViewBox(descriptor, variant)
  return {
    x: box.x + ((clientX - rect.left) / Math.max(rect.width, 1)) * box.width,
    y: box.y + ((clientY - rect.top) / Math.max(rect.height, 1)) * box.height,
  }
}

export function piecePointToCss(
  x: number,
  y: number,
  descriptor?: TowerPieceAssetDescriptor | null,
  variant?: string,
) {
  const box = pieceViewBox(descriptor, variant)
  return {
    left: `${((x - box.x) / Math.max(box.width, 1)) * 100}%`,
    top: `${((y - box.y) / Math.max(box.height, 1)) * 100}%`,
  }
}

function variantDetail(descriptor?: TowerPieceAssetDescriptor | null, variant?: string) {
  const base = descriptor?.tower_piece
  const stateVariant = variant ? base?.state_variants?.[variant] : null
  const variantRecord = isRecord(stateVariant) ? stateVariant : {}
  return {
    viewBox: typeof variantRecord.view_box === 'string' ? variantRecord.view_box : base?.view_box,
    anchors: mergeRecords(base?.anchors, variantRecord.anchors),
    bounds: mergeRecords(base?.bounds, variantRecord.bounds),
  }
}

function parseViewBox(value: string | undefined) {
  const parts = value?.split(/\s+/).map(Number) ?? []
  const x = parts.length === 4 && Number.isFinite(parts[0]) ? parts[0] : 0
  const y = parts.length === 4 && Number.isFinite(parts[1]) ? parts[1] : 0
  const width = parts.length === 4 && Number.isFinite(parts[2]) && parts[2] > 0 ? parts[2] : 100
  const height = parts.length === 4 && Number.isFinite(parts[3]) && parts[3] > 0 ? parts[3] : 100
  return { x, y, width, height }
}

function finiteNumber(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function positiveNumber(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function mergeRecords(
  base: Record<string, unknown> | undefined,
  override: unknown,
): Record<string, unknown> {
  const next = { ...(base ?? {}) }
  if (!isRecord(override)) return next
  for (const [key, value] of Object.entries(override)) next[key] = value
  return next
}
