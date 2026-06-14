import { backendUrl } from '@/shared/api/httpClient'
import type {
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'

type TowerPieceLayerProps = {
  descriptor?: TowerPieceAssetDescriptor | null
  pieceType: TowerPieceType
}

export function TowerPiece({ descriptor, pieceType }: TowerPieceLayerProps) {
  const sprite = defaultSprite(descriptor)
  if (!sprite?.url) {
    // A half-seeded DB (tower-piece assets not seeded) would otherwise render
    // nothing, making the whole tower silently invisible. In dev, surface a
    // labelled placeholder so the cause is obvious; in prod, render nothing.
    if (import.meta.env.DEV) {
      return (
        <span
          className="tower-piece-svg-layer tower-piece-svg-layer--missing"
          data-rendered-piece-type={pieceType}
          aria-hidden="true"
          title={`Missing seeded asset for "${pieceType}". Run: python manage.py seed_assets`}
        >
          {pieceType}
        </span>
      )
    }
    return null
  }
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
