import { backendUrl } from '@/shared/api/httpClient'
import type {
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'

type TowerPieceLayerProps = {
  descriptor?: TowerPieceAssetDescriptor | null
  pieceType: TowerPieceType
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

export function TowerPiece({ descriptor, pieceType }: TowerPieceLayerProps) {
  const sprite = defaultSprite(descriptor)
  if (!sprite?.url) return null
  return (
    <span className="tower-piece-svg-layer" data-rendered-piece-type={pieceType} aria-hidden="true">
      <img className="tower-piece-svg" src={backendUrl(sprite.url)} alt="" draggable={false} />
    </span>
  )
}

export function SpirePiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="spire" />
}

export function LandingPiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="landing" />
}

export function AdventureSectionPiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="adventure_section" />
}

export function ChallengeSectionPiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="challenge_section" />
}

export function DoorPiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="door" />
}

export function TomePiece(props: Omit<TowerPieceLayerProps, 'pieceType'>) {
  return <TowerPiece {...props} pieceType="tome" />
}

function defaultSprite(descriptor?: TowerPieceAssetDescriptor | null) {
  if (!descriptor) return null
  return descriptor.sprites.default ?? Object.values(descriptor.sprites)[0] ?? null
}

function walkRailAnchor(descriptor?: TowerPieceAssetDescriptor | null) {
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

