import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import { PieceArt } from '@/features/tower-map/components/PieceArt'
import { towerDescriptorFor, towerPieceAttrs } from '@/features/tower-map/components/towerPieceData'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { TowerLayoutPieceDescriptor, TowerPieceAssetDescriptor } from '@/shared/assets/types'
import { Button } from '@/shared/components/Button'
import { EmptyState } from '@/shared/components/EmptyState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

/**
 * Renders the player's active private design through the same piece primitives
 * the official tower uses, so the SVG art and the walk-rail data attributes (so
 * Blue can walk the landings) are identical to play mode. It is a faithful
 * preview; content launching lives in a later pass.
 */
export function PrivateTowerStack() {
  const overviewQuery = useQuery({
    queryKey: queryKeys.myTower,
    queryFn: towerDesignsApi.overview,
    retry: false,
  })
  const piecesQuery = useQuery({
    queryKey: queryKeys.assetDescriptorsOwned('tower_piece'),
    queryFn: () => assetsApi.getOwnedDescriptors('tower_piece'),
    staleTime: 5 * 60 * 1000,
  })

  const descriptors = useMemo<Record<string, TowerPieceAssetDescriptor>>(() => {
    const map: Record<string, TowerPieceAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(piecesQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_piece') map[slug] = descriptor
    }
    return map
  }, [piecesQuery.data])

  if (overviewQuery.isLoading) return <LoadingState label="Loading your Spire" variant="page" />

  if (overviewQuery.isError || !overviewQuery.data) {
    return (
      <div className="tower-private-empty">
        <EmptyState
          title="Your Spire isn't raised yet"
          description="Raise and activate your own tower in the editor, then it will rise here."
        />
        <Button asChild className="mt-4 w-fit">
          <Link to="/tower/editor">Open the editor</Link>
        </Button>
      </div>
    )
  }

  return <TowerStack pieces={overviewQuery.data.tower_layout.pieces} descriptors={descriptors} />
}

/**
 * Presentational stack of tower pieces, shared by the owner's private preview
 * and the public shared-tower page. Descriptors must already be resolved
 * (official + any now-public custom pieces).
 */
export function TowerStack({
  pieces,
  descriptors,
}: {
  pieces: TowerLayoutPieceDescriptor[]
  descriptors: Record<string, TowerPieceAssetDescriptor>
}) {
  return (
    <div className="tower-stack-column">
      <div className="learning-tower">
        <div className="tower-repeater">
          {pieces.map((piece) => (
            <PrivatePiece
              key={piece.instanceId}
              piece={piece}
              descriptor={towerDescriptorFor(piece, descriptors)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function PrivatePiece({
  piece,
  descriptor,
}: {
  piece: TowerLayoutPieceDescriptor
  descriptor: TowerPieceAssetDescriptor | null
}) {
  const variant = variantForPrivatePiece(piece)
  const attrs = towerPieceAttrs(piece, descriptor, { variant })

  switch (piece.pieceType) {
    case 'spire':
      return (
        <div className="tower-roof-stage" {...attrs} aria-hidden="true">
          <PieceArt pieceType="spire" descriptor={descriptor} variant={variant} />
        </div>
      )
    case 'window_section':
      return (
        <div className="tower-window-stage" {...attrs} aria-hidden="true">
          <PieceArt pieceType="window_section" descriptor={descriptor} variant={variant} />
        </div>
      )
    case 'landing':
      return (
        <div
          className={cn(
            'tower-landing',
            variant === 'tome' ? 'tower-tome-separator' : 'tower-section-separator',
            variant === 'after-challenges' && 'is-after-challenges',
          )}
          {...attrs}
          aria-hidden="true"
        >
          <PieceArt pieceType="landing" descriptor={descriptor} variant={variant} />
        </div>
      )
    case 'adventure_section':
      return (
        <section className="tower-adventure-stage" {...attrs}>
          <PieceArt pieceType="adventure_section" descriptor={descriptor} variant="adventure" />
          <h2 className="tower-stage-title tower-stage-title--adventure">Command Adventure</h2>
        </section>
      )
    case 'challenge_section':
      return (
        <section className="tower-challenges-stage" {...attrs}>
          <PieceArt pieceType="challenge_section" descriptor={descriptor} variant="challenge" />
          <h2 className="tower-stage-title tower-stage-title--challenge">Challenges</h2>
        </section>
      )
    case 'tome':
      return (
        <section className="tower-tome-stage" {...attrs}>
          <PieceArt pieceType="tome" descriptor={descriptor} />
          <h2 className="tower-stage-title tower-stage-title--tome">Tome</h2>
        </section>
      )
    case 'door':
      return (
        <div className="tower-private-door" {...attrs} aria-hidden="true">
          <PieceArt pieceType="door" descriptor={descriptor} />
        </div>
      )
    default:
      return null
  }
}

function variantForPrivatePiece(piece: TowerLayoutPieceDescriptor) {
  if (piece.pieceType === 'spire') return 'roof'
  if (piece.pieceType === 'window_section') return 'regular'
  if (piece.pieceType === 'landing') {
    if (piece.instanceId.endsWith('landing-after-tomes')) return 'tome'
    if (piece.instanceId.endsWith('landing-after-challenges')) return 'after-challenges'
    return 'regular'
  }
  if (piece.pieceType === 'adventure_section') return 'adventure'
  if (piece.pieceType === 'challenge_section') return 'challenge'
  return undefined
}
