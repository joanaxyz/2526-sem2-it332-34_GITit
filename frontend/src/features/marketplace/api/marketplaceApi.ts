import { apiRequest } from '@/shared/api/httpClient'
import type { ContentDefinition } from '@/features/authoring/types'
import type { WalletSummary } from '@/features/wallet/api/walletApi'

export type MarketplaceListing = {
  id: number
  item_kind: 'asset' | 'content_definition' | 'tower_design'
  item_id: number
  seller_id: number | null
  price: number
  status: 'draft' | 'active' | 'paused' | 'archived'
  owned: boolean
  entitled: boolean
  item: Partial<ContentDefinition> & {
    id?: number
    kind?: string
    slug?: string
    label?: string
    title?: string
    visibility?: string
    tags?: string[]
  }
}

export type MarketplaceListingList = {
  results: MarketplaceListing[]
}

export type PurchaseResult = {
  entitlement: {
    id: number
    item_kind: MarketplaceListing['item_kind']
    asset_id: number | null
    content_definition_id: number | null
    tower_design_id: number | null
    source_listing_id: number | null
    granted_at: string
  }
  wallet: WalletSummary
}

export const marketplaceApi = {
  listings() {
    return apiRequest<MarketplaceListingList>('/marketplace/listings/')
  },
  purchase(listingId: number) {
    return apiRequest<PurchaseResult>(`/marketplace/listings/${listingId}/purchase/`, { method: 'POST' })
  },
}
