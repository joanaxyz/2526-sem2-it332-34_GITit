import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { TowerStack } from '@/features/tower-designs/components/PrivateTowerStack'
import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import { assetsApi } from '@/shared/assets/assetsApi'
import { queryKeys } from '@/shared/api/queryKeys'
import type { TowerArtifactAssetDescriptor, TowerPieceAssetDescriptor } from '@/shared/assets/types'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

/**
 * Public, read-only view of a shared personal tower. No auth required — the
 * backend only serves published + public personal designs. Custom pieces are
 * resolvable here because sharing publishes the author's referenced assets.
 */
export function SharedTowerPage() {
  const { designId } = useParams()
  const id = designId ? Number(designId) : null

  const overviewQuery = useQuery({
    queryKey: queryKeys.sharedTower(id ?? 0),
    queryFn: () => towerDesignsApi.sharedOverview(id as number),
    enabled: id !== null,
    retry: false,
  })
  const piecesQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('tower_piece'),
    queryFn: () => assetsApi.getDescriptors('tower_piece'),
    staleTime: 5 * 60 * 1000,
  })
  const artifactsQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('tower_artifact'),
    queryFn: () => assetsApi.getDescriptors('tower_artifact'),
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

  if (id === null) return <ErrorState title="Tower not found" description="This share link is invalid." />
  if (overviewQuery.isLoading) return <LoadingState label="Loading tower" variant="page" />
  if (overviewQuery.isError || !overviewQuery.data) {
    return (
      <ErrorState
        title="Tower not found"
        description="This tower is private or no longer shared."
      />
    )
  }

  const { design, tower_layout, artifacts } = overviewQuery.data
  return (
    <div className="shared-tower-page">
      <header className="shared-tower-head">
        <p className="shared-tower-kicker">A shared Spire</p>
        <h1 className="shared-tower-title">{design.title}</h1>
        {design.summary ? <p className="shared-tower-summary">{design.summary}</p> : null}
      </header>
      <TowerStack
        pieces={tower_layout.pieces}
        artifacts={artifacts}
        descriptors={descriptors}
        artifactDescriptors={artifactDescriptors}
      />
    </div>
  )
}

export default SharedTowerPage
