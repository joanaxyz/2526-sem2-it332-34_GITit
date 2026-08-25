import { queryOptions } from '@tanstack/react-query'

import type {
  ApiRequestBody,
  ApiResponseBody,
  ApiSchemas,
} from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'

export type ShopCatalog = ApiResponseBody<'shop_catalog_retrieve'>
export type ShopItem = ShopCatalog['items'][number]
export type ShopKind = ApiSchemas['ShopItemResponseKindEnum']
export type ShopPurchaseResult = ApiResponseBody<'shop_catalog_purchase_create'>

type ShopPurchasePayload = ApiRequestBody<'shop_catalog_purchase_create'>

export const shopApi = {
  catalog() {
    return apiOperationRequest('shop_catalog_retrieve', '/shop/catalog/')
  },
  purchase(kind: ShopKind, slug: string) {
    const body = { kind, slug } satisfies ShopPurchasePayload
    return apiOperationRequest(
      'shop_catalog_purchase_create',
      '/shop/catalog/purchase/',
      { body },
    )
  },
}

export function shopCatalogQueryOptions() {
  return queryOptions({
    queryKey: queryKeys.shopCatalog,
    queryFn: shopApi.catalog,
    staleTime: 60_000,
  })
}
