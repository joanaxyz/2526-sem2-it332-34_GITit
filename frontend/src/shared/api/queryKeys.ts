import type { StoreyContentSection } from '@/features/challenges/types'
import type { AssetKind } from '@/shared/assets/types'

export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  homeSummary: ['home-summary'] as const,
  statsSummary: ['stats-summary'] as const,
  wallet: ['wallet'] as const,
  storeys: ['storeys'] as const,
  authoringContent: (kind?: string) => ['authoring-content', kind ?? 'all'] as const,
  authoringContentDetail: (id: number) => ['authoring-content-detail', id] as const,
  authoringStoreys: ['authoring-storeys'] as const,
  towerDesigns: ['tower-designs'] as const,
  towerDesignLayout: (id: number) => ['tower-design-layout', id] as const,
  myTower: ['my-tower'] as const,
  sharedTower: (id: number) => ['shared-tower', id] as const,
  marketplaceListings: ['marketplace-listings'] as const,
  galleryAssets: ['gallery-assets'] as const,
  galleryContent: ['gallery-content'] as const,
  galleryTowerDesigns: ['gallery-tower-designs'] as const,
  assetDescriptors: (kind: AssetKind) => ['asset-descriptors', kind] as const,
  assetDescriptorsOwned: (kind: AssetKind) => ['asset-descriptors-owned', kind] as const,
  storeyContent: (storeyId: number | null | undefined, section: StoreyContentSection) =>
    ['storey-content', storeyId, section] as const,
  storeyOverview: (storeyId: number | null | undefined) => ['storey-overview', storeyId] as const,
  learnedSkills: ['learned-skills'] as const,
  storeyBook: (storeyId: number | null | undefined) => ['storey-book', storeyId] as const,
  commandFormPreview: (formId: number) => ['command-form-preview', formId] as const,
  challengeRun: (runId: number) => ['challenge-run', runId] as const,
  adventureRun: (runId: number) => ['adventure-run', runId] as const,
}

export const queryKeyRoots = {
  storeyContent: ['storey-content'] as const,
  storeyOverview: ['storey-overview'] as const,
}
