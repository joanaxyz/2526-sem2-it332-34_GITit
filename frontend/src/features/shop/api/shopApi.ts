import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  ShopCatalogResponse,
  ShopItem,
  ShopKind,
  ShopPurchaseResult,
  UnlocksStory,
} from '@/features/shop/types'

export type {
  ShopCatalogResponse,
  ShopItem,
  ShopKind,
  ShopPurchaseResult,
  UnlocksStory,
}

export const shopApi = {
  catalog() {
    return apiOperationRequest<'shop_catalog_retrieve', ShopCatalogResponse>('shop_catalog_retrieve', '/shop/catalog/')
  },
  purchase(kind: ShopKind, slug: string) {
    return apiOperationRequest<'shop_catalog_purchase_create', ShopPurchaseResult>(
      'shop_catalog_purchase_create',
      '/shop/catalog/purchase/',
      { body: { kind, slug } },
    )
  },
}
