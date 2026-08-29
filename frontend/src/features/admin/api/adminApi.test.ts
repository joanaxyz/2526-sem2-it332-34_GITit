import { afterEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api/httpClient', () => ({
  apiOperationRequest: vi.fn().mockResolvedValue({}),
}))

import { apiOperationRequest } from '@/shared/api/httpClient'

import { adminApi } from './adminApi'

const request = vi.mocked(apiOperationRequest)

describe('adminApi generated operations', () => {
  afterEach(() => vi.clearAllMocks())

  it('uses the named overview and story operations', () => {
    adminApi.overview()
    adminApi.stories()

    expect(request).toHaveBeenNthCalledWith(
      1,
      'admin_overview_retrieve',
      '/admin/overview/',
    )
    expect(request).toHaveBeenNthCalledWith(
      2,
      'admin_stories_retrieve',
      '/admin/stories/',
    )
  })

  it('keeps economy idempotency data in the generated request body', () => {
    const payload = {
      user_id: 7,
      amount: 250,
      reason: 'support_adjustment',
      request_id: 'a93767f4-5f40-45cd-8a94-8a3f3c7ae486',
    }

    adminApi.adjustCoins(payload)

    expect(request).toHaveBeenCalledWith(
      'admin_economy_adjust_create',
      '/admin/economy/adjust/',
      { body: payload },
    )
  })

  it('uses generated mutation operations for chapters and settings', () => {
    const chapter = {
      story_id: 4,
      slug: 'safe-chapter',
      number: 2,
      title: 'Safe Chapter',
    }
    adminApi.createChapter(chapter)
    adminApi.saveFlag({ key: 'shop-purchases', enabled: false })

    expect(request).toHaveBeenNthCalledWith(
      1,
      'admin_chapters_create',
      '/admin/chapters/',
      { body: chapter },
    )
    expect(request).toHaveBeenNthCalledWith(
      2,
      'admin_settings_create',
      '/admin/settings/',
      { body: { key: 'shop-purchases', enabled: false } },
    )
  })
})
