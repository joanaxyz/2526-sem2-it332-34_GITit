import { pieceViewBoxString } from '@/features/tower-map/components/towerPieceData'
import { PieceSvg } from '@/features/tower-map/pieces/PieceSvg'
import { resolvePieceArt } from '@/features/tower-map/pieces/resolvePieceArt'
import type { TowerPieceAssetDescriptor } from '@/shared/assets/types'

/**
 * Renders a tower piece from its asset's inline SVG. The art (shape, colour,
 * animation) is owned entirely by the asset — the frontend never re-draws or
 * recolours a piece, it only positions the SVG and applies the named animation
 * preset. When a descriptor has no SVG yet (e.g. a fresh user upload, or a DB
 * that hasn't run `seed_assets`), there is deliberately no fallback art: dev
 * surfaces a labelled placeholder so the missing seed is obvious; prod renders
 * nothing rather than substituting some other piece's art.
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
        animation={resolved.animation}
        className={classNameFor(pieceType, renderVariant)}
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

function classNameFor(pieceType: string, variant?: string) {
  switch (pieceType) {
    case 'spire':
      return 'tower-roof-art'
    case 'window_section':
      return 'tower-window-band-art'
    case 'landing':
      return variant === 'tome' ? 'tower-landing-art tower-landing-art--tome' : 'tower-landing-art'
    case 'adventure_section':
    case 'challenge_section':
      return 'tower-hall-art'
    case 'tome':
      return 'tome-lectern-art'
    case 'door':
      return variant === 'portcullis' ? 'trial-door-art' : 'adventure-door-art'
    default:
      return undefined
  }
}

function defaultVariantFor(pieceType: string) {
  switch (pieceType) {
    case 'spire':
      return 'roof'
    case 'window_section':
      return 'regular'
    case 'landing':
      return 'regular'
    case 'adventure_section':
      return 'adventure'
    case 'challenge_section':
      return 'challenge'
    default:
      return undefined
  }
}
