import type { ContentDefinition } from '@/features/authoring/types'
import type { TowerLayoutDescriptor } from '@/shared/assets/types'

export type TowerDesign = {
  id: number
  owner_id: number | null
  source_design_id: number | null
  visibility: 'private' | 'public' | 'store'
  status: 'draft' | 'published' | 'archived'
  slug: string
  title: string
  summary: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type TowerDesignList = {
  results: TowerDesign[]
}

export type ArtifactPlacementDescriptor = {
  id: number
  targetInstanceId: string
  assetSlug: string
  x: number
  y: number
  scale: number
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
