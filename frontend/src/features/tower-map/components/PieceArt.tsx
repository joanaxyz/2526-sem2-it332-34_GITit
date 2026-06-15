import { pieceViewBoxString } from '@/features/tower-map/components/towerPieceData'
import { PieceSvg } from '@/features/tower-map/pieces/PieceSvg'
import { resolvePieceArt } from '@/features/tower-map/pieces/resolvePieceArt'
import type { TowerPieceAssetDescriptor } from '@/shared/assets/types'

/**
 * Renders structural tower art from asset-owned SVG data. Structural pieces are
 * deliberately generic: crown, section, and landing.
 */
export function PieceArt({
  pieceType,
  descriptor,
  variant,
}: {
  pieceType: string
  descriptor?: TowerPieceAssetDescriptor | null
  variant?: string
}) {
  const renderVariant = variant ?? defaultVariantFor(pieceType)
  const resolved = resolvePieceArt(descriptor)
  if (resolved) {
    return (
      <PieceSvg
        svg={resolved.svg}
        className={classNameFor(pieceType)}
        viewBox={pieceViewBoxString(descriptor, renderVariant)}
        variant={renderVariant}
      />
    )
  }

  if (import.meta.env.DEV) {
    return (
      <span
        className="piece-art-missing"
        data-rendered-piece-type={pieceType}
        aria-hidden="true"
        title={`Missing art for "${pieceType}". Run: python manage.py seed_assets`}
      >
        {pieceType}
      </span>
    )
  }
  return null
}

function classNameFor(pieceType: string) {
  switch (pieceType) {
    case 'crown':
      return 'tower-roof-art'
    case 'landing':
      return 'tower-landing-art'
    case 'section':
      return 'tower-hall-art'
    default:
      return undefined
  }
}

function defaultVariantFor(pieceType: string) {
  switch (pieceType) {
    case 'crown':
      return 'roof'
    case 'landing':
      return 'regular'
    case 'section':
      return 'regular'
    default:
      return undefined
  }
}
