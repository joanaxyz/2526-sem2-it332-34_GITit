import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import type { ArtifactPlacementDescriptor } from '@/features/tower-designs/types'
import { RoofSpire, TowerLanding, TowerSectionShell } from '@/features/tower-map/components/TowerStoreySection'
import { TowerArtifact } from '@/features/tower-map/components/TowerArtifact'
import { pieceVariant, towerDescriptorFor } from '@/features/tower-map/components/towerPieceData'
import { assetsApi } from '@/shared/assets/assetsApi'
import type {
  TowerArtifactAssetDescriptor,
  TowerArtifactRole,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { Button } from '@/shared/components/Button'
import { EmptyState } from '@/shared/components/EmptyState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

/**
 * Renders the player's active private design through the same generalized piece
 * primitives the official tower uses. The preview is intentionally read-only:
 * content launching belongs to play mode, while this view verifies the authored
 * composition and uploaded asset data.
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
  const artifactsQuery = useQuery({
    queryKey: queryKeys.assetDescriptorsOwned('tower_artifact'),
    queryFn: () => assetsApi.getOwnedDescriptors('tower_artifact'),
    staleTime: 5 * 60 * 1000,
  })

  const descriptors = useMemo<Record<string, TowerPieceAssetDescriptor>>(() => {
    const map: Record<string, TowerPieceAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(piecesQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_piece') map[slug] = descriptor
    }
    return map
  }, [piecesQuery.data])

  const artifactDescriptors = useMemo<Record<string, TowerArtifactAssetDescriptor>>(() => {
    const map: Record<string, TowerArtifactAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(artifactsQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_artifact') map[slug] = descriptor
    }
    return map
  }, [artifactsQuery.data])

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

  return (
    <TowerStack
      pieces={overviewQuery.data.tower_layout.pieces}
      artifacts={overviewQuery.data.artifacts}
      descriptors={descriptors}
      artifactDescriptors={artifactDescriptors}
    />
  )
}

/**
 * Presentational stack of tower pieces, shared by the owner's private preview
 * and the public shared-tower page. Descriptors must already be resolved
 * (official + any now-public custom pieces).
 */
export function TowerStack({
  pieces,
  artifacts = [],
  descriptors,
  artifactDescriptors = {},
}: {
  pieces: TowerLayoutPieceDescriptor[]
  artifacts?: ArtifactPlacementDescriptor[]
  descriptors: Record<string, TowerPieceAssetDescriptor>
  artifactDescriptors?: Record<string, TowerArtifactAssetDescriptor>
}) {
  const artifactsByInstance = useMemo(() => groupArtifacts(artifacts), [artifacts])

  return (
    <div className="tower-stack-column">
      <div className="learning-tower">
        <div className="tower-repeater">
          {pieces.map((piece) => {
            const descriptor = towerDescriptorFor(piece, descriptors)
            const placements = artifactsByInstance.get(piece.instanceId) ?? []
            const role = firstInteractableRole(placements)
            const children = placements.map((artifact) => (
              <TowerArtifact
                key={artifact.id}
                artifact={artifact}
                descriptor={artifactDescriptors[artifact.assetSlug] ?? null}
                pieceDescriptor={descriptor}
                pieceVariant={role === 'normal' ? pieceVariant(null, piece) : role}
              />
            ))

            if (piece.pieceType === 'crown') {
              return (
                <RoofSpire key={piece.instanceId} piece={piece} descriptor={descriptor}>
                  {children}
                </RoofSpire>
              )
            }

            if (piece.pieceType === 'landing') {
              return (
                <TowerLanding key={piece.instanceId} piece={piece} descriptor={descriptor} variant={pieceVariant(null, piece)}>
                  {children}
                </TowerLanding>
              )
            }

            return (
              <TowerSectionShell key={piece.instanceId} piece={piece} descriptor={descriptor} artifactRole={role}>
                {children}
              </TowerSectionShell>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function firstInteractableRole(artifacts: ArtifactPlacementDescriptor[]): TowerArtifactRole {
  return artifacts.find((artifact) => artifact.role !== 'normal')?.role ?? 'normal'
}

function groupArtifacts(artifacts: ArtifactPlacementDescriptor[]) {
  const map = new Map<string, ArtifactPlacementDescriptor[]>()
  for (const artifact of artifacts) {
    const list = map.get(artifact.targetInstanceId) ?? []
    list.push(artifact)
    map.set(artifact.targetInstanceId, list)
  }
  return map
}
