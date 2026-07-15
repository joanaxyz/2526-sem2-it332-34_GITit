import type { WalletSummary } from '@/shared/wallet/api/walletApi'

export type ShopKind = 'story' | 'companion'

export type UnlocksStory = {
  slug: string
  title: string
  chapter_count: number
  world_slug?: string
  difficulty?: 'beginner' | 'advanced' | 'expert'
  prerequisite_story?: string | null
}

export type ShopItem = {
  kind: ShopKind
  slug: string
  label: string
  price: number
  owned: boolean
  active: boolean
  /** Present only on story items: the story this purchase unlocks. */
  unlocks_story?: UnlocksStory | null
}

export type ShopCatalogResponse = {
  items: ShopItem[]
  /** Null until the player owns and equips a companion - no companion is free. */
  active_companion: string | null
}

export type ShopPurchaseResult = {
  owned: boolean
  wallet: WalletSummary
  shop: ShopCatalogResponse
}

export type ShopEquipResult = {
  active_companion: string | null
  shop: ShopCatalogResponse
}

