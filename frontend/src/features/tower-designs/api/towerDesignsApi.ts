import { apiRequest } from '@/shared/api/httpClient'
import type {
  ArtifactPlacementPayload,
  TowerContentBindingPayload,
  TowerDesign,
  TowerDesignList,
  TowerDesignOverview,
  TowerPieceInstancePayload,
} from '@/features/tower-designs/types'
import type { TowerArtifactRole } from '@/shared/assets/types'

export const towerDesignsApi = {
  mine() {
    return apiRequest<TowerDesignList>('/tower-designs/mine/')
  },
  create(input: { slug: string; title: string; summary?: string }) {
    return apiRequest<TowerDesign>('/tower-designs/', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  update(id: number, input: Partial<Pick<TowerDesign, 'title' | 'summary' | 'visibility'>>) {
    return apiRequest<TowerDesign>(`/tower-designs/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
  setActive(id: number) {
    return apiRequest<TowerDesign>(`/tower-designs/${id}/set-active/`, { method: 'POST' })
  },
  publish(id: number) {
    return apiRequest<TowerDesign>(`/tower-designs/${id}/publish/`, { method: 'POST' })
  },
  share(id: number) {
    return apiRequest<TowerDesign>(`/tower-designs/${id}/share/`, { method: 'POST' })
  },
  /** Get-or-create the user's private fork of the official tower. */
  officialFork() {
    return apiRequest<TowerDesignOverview>('/tower-designs/official-fork/', { method: 'POST' })
  },
  remix(id: number) {
    return apiRequest<TowerDesignOverview>(`/tower-designs/${id}/remix/`, { method: 'POST' })
  },
  overview() {
    return apiRequest<TowerDesignOverview>('/my-tower/overview/')
  },
  /** Public, read-only overview of a shared personal tower (no auth required). */
  sharedOverview(id: number) {
    return apiRequest<TowerDesignOverview>(`/tower-designs/shared/${id}/`)
  },
  layout(id: number) {
    return apiRequest<TowerDesignOverview>(`/tower-designs/${id}/layout/`)
  },

  /** Append a new storey (floor) of pieces; returns the updated overview. */
  addStorey(designId: number) {
    return apiRequest<TowerDesignOverview & { added_storey_index: number }>(
      `/tower-designs/${designId}/storeys/`,
      { method: 'POST' },
    )
  },

  // --- Pieces (structural slots) ---
  addPiece(
    designId: number,
    input: {
      piece_asset_id: number
      piece_type: string
      sort_order?: number
      storey_index?: number
      parent_instance_id?: number | null
      transform?: Record<string, unknown>
      config?: Record<string, unknown>
    },
  ) {
    return apiRequest<TowerPieceInstancePayload>(`/tower-designs/${designId}/pieces/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  updatePiece(
    designId: number,
    pieceId: number,
    input: {
      piece_asset_id?: number
      sort_order?: number
      transform?: Record<string, unknown>
      config?: Record<string, unknown>
    },
  ) {
    return apiRequest<TowerPieceInstancePayload>(`/tower-designs/${designId}/pieces/${pieceId}/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
  deletePiece(designId: number, pieceId: number) {
    return apiRequest<null>(`/tower-designs/${designId}/pieces/${pieceId}/`, { method: 'DELETE' })
  },

  // --- Content bindings (adventure/challenge/tome -> section piece) ---
  bindContent(designId: number, input: { piece_instance_id: number; content_definition_id: number }) {
    return apiRequest<TowerContentBindingPayload>(`/tower-designs/${designId}/bindings/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  unbindContent(designId: number, bindingId: number) {
    return apiRequest<null>(`/tower-designs/${designId}/bindings/${bindingId}/`, { method: 'DELETE' })
  },

  // --- Artifact placements (free-drag decorative overlays) ---
  placeArtifact(
    designId: number,
    input: {
      target_piece_instance_id: number
      artifact_asset_id: number
      role?: TowerArtifactRole
      content_definition_id?: number | null
      x?: number
      y?: number
      scale?: number
      width?: number
      height?: number
      rotation?: number
      anchor?: string
      z_index?: number
    },
  ) {
    return apiRequest<ArtifactPlacementPayload>(`/tower-designs/${designId}/artifacts/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  updateArtifact(
    designId: number,
    placementId: number | string,
    input: {
      x?: number
      y?: number
      scale?: number
      width?: number
      height?: number
      rotation?: number
      anchor?: string
      z_index?: number
      role?: TowerArtifactRole
      content_definition_id?: number | null
    },
  ) {
    return apiRequest<ArtifactPlacementPayload>(`/tower-designs/${designId}/artifacts/${placementId}/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
  deleteArtifact(designId: number, placementId: number) {
    return apiRequest<null>(`/tower-designs/${designId}/artifacts/${placementId}/`, { method: 'DELETE' })
  },
}
