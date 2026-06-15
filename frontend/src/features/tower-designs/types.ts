import type { ContentDefinition } from '@/features/authoring/types'
import type { TowerArtifactRole, TowerContentBinding, TowerLayoutDescriptor } from '@/shared/assets/types'

export type TowerOrigin = 'personal' | 'official_fork'

export type TowerDesign = {
  id: number
  owner_id: number | null
  source_design_id: number | null
  visibility: 'private' | 'public' | 'store'
  status: 'draft' | 'published' | 'archived'
  origin: TowerOrigin
  slug: string
  title: string
  summary: string
  is_active: boolean
  created_at: string
  updated_at: string
  /** Present on the share() response. */
  share_path?: string
}

export type TowerDesignList = {
  results: TowerDesign[]
}

export type ArtifactPlacementDescriptor = {
  id: number | string
  targetInstanceId: string
  assetSlug: string
  role: TowerArtifactRole
  contentBinding?: TowerContentBinding | null
  x: number
  y: number
  scale: number
  width: number
  height: number
  rotation: number
  anchor: string
  zIndex: number
}

export type TowerDesignOverview = {
  design: TowerDesign
  tower_layout: TowerLayoutDescriptor & { designId?: number | null }
  content: {
    adventures: Record<string, ContentDefinition>
    challenges: Record<string, ContentDefinition>
    tomes: Record<string, ContentDefinition>
  }
  artifacts: ArtifactPlacementDescriptor[]
}

/** Raw piece/binding/artifact rows returned by the mutation endpoints. */
export type TowerPieceInstancePayload = {
  id: number
  tower_design_id: number
  piece_asset_id: number
  piece_type: string
  storey_index: number
  sort_order: number
  parent_instance_id: number | null
  transform: Record<string, unknown>
  config: Record<string, unknown>
}

export type TowerContentBindingPayload = {
  id: number
  piece_instance_id: number
  content_definition_id: number
}

export type ArtifactPlacementPayload = {
  id: number
  tower_design_id: number
  target_piece_instance_id: number
  artifact_asset_id: number
  x: number
  y: number
  scale: number
  width: number
  height: number
  rotation: number
  anchor: string
  z_index: number
  role: TowerArtifactRole
  content_definition_id: number | null
}
