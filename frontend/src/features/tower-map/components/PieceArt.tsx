import { pieceViewBoxString } from '@/features/tower-map/components/towerPieceData'
import { PieceSvg } from '@/features/tower-map/pieces/PieceSvg'
import { resolvePieceArt } from '@/features/tower-map/pieces/resolvePieceArt'
import { backendUrl } from '@/shared/api/httpClient'
import type { TowerPieceAssetDescriptor } from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

/**
 * Renders structural tower art from asset-owned SVG data. Structural pieces are
 * deliberately generic: crown, base, section, and landing.
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

  const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)
  if (sprite?.url) {
    return (
      <img
        className={cn('piece-image', classNameFor(pieceType), sprite.is_raster && 'piece-art--raster')}
        data-piece-variant={renderVariant}
        data-piece-content-type={sprite.content_type}
        src={backendUrl(sprite.url)}
        alt=""
        draggable={false}
        aria-hidden="true"
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
    case 'base':
      return 'tower-base-art'
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
    case 'base':
      return 'base'
    case 'landing':
      return 'regular'
    case 'section':
      return 'regular'
    default:
      return undefined
  }
}
