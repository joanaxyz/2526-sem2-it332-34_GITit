import { afterEach, describe, expect, expectTypeOf, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import {
  shopApi,
  shopCatalogQueryOptions,
  type ShopCatalog,
} from '@/shared/shop/api/shopApi'

const mockedApiRequest = vi.mocked(apiOperationRequest)

describe('shopApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('owns the operation-aware catalog query', () => {
    const options = shopCatalogQueryOptions()
    options.queryFn?.({} as never)

    expect(options.queryKey).toEqual(queryKeys.shopCatalog)
    expect(options.staleTime).toBe(60_000)
    expect(mockedApiRequest).toHaveBeenCalledWith(
      'shop_catalog_retrieve',
      '/shop/catalog/',
    )
  })

  it('keeps purchases explicit in the generated request payload', () => {
    shopApi.purchase('story', 'arcane-spire')

    expect(mockedApiRequest).toHaveBeenCalledWith(
      'shop_catalog_purchase_create',
      '/shop/catalog/purchase/',
      { body: { kind: 'story', slug: 'arcane-spire' } },
    )
  })

  it('derives story unlock difficulty from the generated contract', () => {
    type StoryUnlock = NonNullable<ShopCatalog['items'][number]['unlocks_story']>
    expectTypeOf<StoryUnlock['difficulty']>().toEqualTypeOf<
      'beginner' | 'intermediate' | 'advanced'
    >()
  })
})
