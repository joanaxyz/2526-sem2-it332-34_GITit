import type {
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'

export function towerDescriptorFor(
  piece: TowerLayoutPieceDescriptor | null | undefined,
  descriptors: Record<string, TowerPieceAssetDescriptor>,
) {
  return piece ? descriptors[piece.assetSlug] ?? null : null
}

export function towerPieceAttrs(
  piece: TowerLayoutPieceDescriptor | null | undefined,
  descriptor?: TowerPieceAssetDescriptor | null,
) {
  const rail = walkRailAnchor(descriptor)
  const viewBox = viewBoxSize(descriptor?.tower_piece?.view_box)
  return {
    'data-piece-id': piece?.instanceId,
    'data-asset-slug': piece?.assetSlug,
    'data-piece-type': piece?.pieceType,
    'data-viewbox-width': rail ? viewBox.width : undefined,
    'data-viewbox-height': rail ? viewBox.height : undefined,
    'data-walk-rail-x1': rail?.x1,
    'data-walk-rail-y1': rail?.y1,
    'data-walk-rail-x2': rail?.x2,
    'data-walk-rail-y2': rail?.y2,
  }
}

/** Whether a piece asset carries a valid walk_rail anchor, i.e. Blue can stand on it. */
export function pieceHasWalkRail(descriptor?: TowerPieceAssetDescriptor | null) {
  return walkRailAnchor(descriptor) !== null
}

export function walkRailAnchor(descriptor?: TowerPieceAssetDescriptor | null) {
  const rail = descriptor?.tower_piece?.anchors.walk_rail
  if (!isRecord(rail)) return null
  const x1 = finiteNumber(rail.x1)
  const y1 = finiteNumber(rail.y1)
  const x2 = finiteNumber(rail.x2)
  const y2 = finiteNumber(rail.y2)
  if ([x1, y1, x2, y2].some((value) => value === null)) return null
  return { x1, y1, x2, y2 }
}

function viewBoxSize(value: string | undefined) {
  const parts = value?.split(/\s+/).map(Number) ?? []
  const width = parts.length === 4 && Number.isFinite(parts[2]) && parts[2] > 0 ? parts[2] : 100
  const height = parts.length === 4 && Number.isFinite(parts[3]) && parts[3] > 0 ? parts[3] : 100
  return { width, height }
}

function finiteNumber(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}
