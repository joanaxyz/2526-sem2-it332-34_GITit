import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'
import { shopApi } from './shopApi'

const mockedApiRequest = vi.mocked(apiOperationRequest)

describe('shopApi', () => {
  afterEach(() => vi.clearAllMocks())

  it('loads the story and companion shop catalog', () => {
    shopApi.catalog()

    expect(mockedApiRequest).toHaveBeenCalledWith('shop_catalog_retrieve', '/shop/catalog/')
  })

  it('keeps purchases explicit in the payload', () => {
    shopApi.purchase('story', 'arcane-spire')

    expect(mockedApiRequest).toHaveBeenCalledWith(
      'shop_catalog_purchase_create',
      '/shop/catalog/purchase/',
      { body: { kind: 'story', slug: 'arcane-spire' } },
    )
  })
})
