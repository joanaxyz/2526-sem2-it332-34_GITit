import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import { pieceIdFromInstance } from '@/features/tower-designs/editorUtils'
import { assetsApi } from '@/shared/assets/assetsApi'
import { queryKeys } from '@/shared/api/queryKeys'
import type {
  TowerArtifactRole,
  TowerArtifactAssetDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'

export function useDesignEditor(designId: number) {
  const queryClient = useQueryClient()

  const layoutQuery = useQuery({
    queryKey: queryKeys.towerDesignLayout(designId),
    queryFn: () => towerDesignsApi.layout(designId),
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

  const pieceDescriptors = useMemo<TowerPieceAssetDescriptor[]>(() => {
    return Object.values(piecesQuery.data?.results ?? {}).filter(
      (d): d is TowerPieceAssetDescriptor => d.kind === 'tower_piece',
    )
  }, [piecesQuery.data])

  const pieceDescriptorBySlug = useMemo<Record<string, TowerPieceAssetDescriptor>>(() => {
    const map: Record<string, TowerPieceAssetDescriptor> = {}
    for (const d of pieceDescriptors) map[d.slug] = d
    return map
  }, [pieceDescriptors])

  const artifactDescriptors = useMemo<TowerArtifactAssetDescriptor[]>(() => {
    return Object.values(artifactsQuery.data?.results ?? {}).filter(
      (d): d is TowerArtifactAssetDescriptor => d.kind === 'tower_artifact',
    )
  }, [artifactsQuery.data])

  const artifactDescriptorBySlug = useMemo<Record<string, TowerArtifactAssetDescriptor>>(() => {
    const map: Record<string, TowerArtifactAssetDescriptor> = {}
    for (const d of artifactDescriptors) map[d.slug] = d
    return map
  }, [artifactDescriptors])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: queryKeys.towerDesignLayout(designId) })
    queryClient.invalidateQueries({ queryKey: queryKeys.myTower })
  }

  const rename = useMutation({
    mutationFn: (title: string) => towerDesignsApi.update(designId, { title }),
    onSuccess: () => {
      invalidate()
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
    },
  })
  const swapAsset = useMutation({
    mutationFn: ({ pieceId, assetId }: { pieceId: number; assetId: number }) =>
      towerDesignsApi.updatePiece(designId, pieceId, { piece_asset_id: assetId }),
    onSuccess: invalidate,
  })
  const updatePiece = useMutation({
    mutationFn: ({
      pieceId,
      input,
    }: {
      pieceId: number
      input: Parameters<typeof towerDesignsApi.updatePiece>[2]
    }) => towerDesignsApi.updatePiece(designId, pieceId, input),
    onSuccess: invalidate,
  })
  const addPiece = useMutation({
    mutationFn: (input: {
      piece_asset_id: number
      piece_type: string
      sort_order?: number
      storey_index?: number
      parent_instance_id?: number | null
      config?: Record<string, unknown>
    }) =>
      towerDesignsApi.addPiece(designId, input),
    onSuccess: invalidate,
  })
  const addStorey = useMutation({
    mutationFn: () => towerDesignsApi.addStorey(designId),
    onSuccess: invalidate,
  })
  const deletePiece = useMutation({
    mutationFn: (pieceId: number) => towerDesignsApi.deletePiece(designId, pieceId),
    onSuccess: invalidate,
  })
  const bind = useMutation({
    mutationFn: (input: { piece_instance_id: number; content_definition_id: number }) =>
      towerDesignsApi.bindContent(designId, input),
    onSuccess: invalidate,
  })
  const unbind = useMutation({
    mutationFn: (bindingId: number) => towerDesignsApi.unbindContent(designId, bindingId),
    onSuccess: invalidate,
  })
  const placeArtifact = useMutation({
    mutationFn: (input: {
      target_piece_instance_id: number
      artifact_asset_id: number
      role?: TowerArtifactRole
      content_definition_id?: number | null
      x?: number
      y?: number
      width?: number
      height?: number
    }) =>
      towerDesignsApi.placeArtifact(designId, input),
    onSuccess: invalidate,
  })
  const updateArtifact = useMutation({
    mutationFn: ({ placementId, ...input }: {
      placementId: number | string
      target_piece_instance_id?: number
      x?: number
      y?: number
      scale?: number
      width?: number
      height?: number
      rotation?: number
      z_index?: number
      role?: TowerArtifactRole
      content_definition_id?: number | null
    }) =>
      towerDesignsApi.updateArtifact(designId, placementId, input),
    onSuccess: invalidate,
  })
  const deleteArtifact = useMutation({
    mutationFn: (placementId: number) => towerDesignsApi.deleteArtifact(designId, placementId),
    onSuccess: invalidate,
  })
  const publish = useMutation({
    mutationFn: () => towerDesignsApi.publish(designId),
    onSuccess: () => {
      invalidate()
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
    },
  })
  const share = useMutation({
    mutationFn: () => towerDesignsApi.share(designId),
    onSuccess: () => {
      invalidate()
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
    },
  })

  return {
    overview: layoutQuery.data ?? null,
    isLoading: layoutQuery.isLoading,
    isError: layoutQuery.isError,
    error: layoutQuery.error,
    /** Await a fresh layout — used after Apply so staged edits are cleared only
     *  once the server values have landed (no flash back to the old transform). */
    refetchLayout: () => layoutQuery.refetch(),
    pieceDescriptors,
    pieceDescriptorBySlug,
    artifactDescriptors,
    artifactDescriptorBySlug,
    pieceIdFromInstance,
    rename,
    swapAsset,
    updatePiece,
    addPiece,
    addStorey,
    deletePiece,
    bind,
    unbind,
    placeArtifact,
    updateArtifact,
    deleteArtifact,
    publish,
    share,
  }
}
